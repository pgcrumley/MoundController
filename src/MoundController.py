#!/usr/bin/python3
"""
MIT License

Copyright (c) 2017, 2018 Paul G Crumley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: pgcrumley@gmail.com

Control a pump which moves water through a compost pile by capturing
data from DS18B20 sensors which are attached to
Arduinos accessed by serial ports.

This code assumes the controllers use either the 
    DS18B20_SampleOnDemand
or
    DS18B20_Fast_SampleOnDemand 
sketches as the communication protocol for both is the same.  (e.g. send NL
then retrieve data till an empty line is received)

The sensors are segregated in to two groups:
  "watched" sensors are used to control the state of the pump
  "monitored" sensors are used to collect data on the temperature of the pile
  
  The "monitored" sensors are continually sampled at a base frequency.
  
  When the pump is running the "watched" sensors are sampled more often to 
  capture more data on the amount of energy being removed from the pile.
  
  The pumping algorithm is a loop which does the following:
    Start the pump (and faster samples on watched sensors)
    Let the water circulate for 30 seconds.
    Each time the watched sensors are read, record the output temperature
    While the temperature is above PUMP_THRESHOLD
      keep pumping
    When the temperature is at or below PUMP_THRESHOLD
      Turn off the pump
      Return the sampling rate of the watched sensors to the monitor rate
      Wait 120 minutes
    Loop back to the top of this sequence 

"""

import datetime
import glob
import queue
import serial
import sys
import threading
import time

import RPi.GPIO as GPIO

DEBUG = 0
SMS = 0

if SMS:
    from twilio.rest import Client as TwilioClient

# sample sensors a bit more often than once a minute
BASE_SAMPLE_INTERVAL_IN_SECONDS = 58
# sample this often when running pump
PUMPING_SAMPLE_INTERVAL_IN_SECONDS = 4 # NOTE: Could be hard of > 2 ports
# how long to wait after changing sample rate
START_STOP_SECONDS = 2 * PUMPING_SAMPLE_INTERVAL_IN_SECONDS

# wait this long after stopping pump to let pile heat up again
REHEAT_TIME_IN_SECONDS = 1.5 * 60 * 60 # 1.5 hour * 60 min / hour * 60 sec / min

# Run pump till output temperature is this low
#PUMP_THRESHOLD_TEMPERATURE = 53 # 35 degrees C, about 127 degrees F
PUMP_THRESHOLD_TEMPERATURE = 40 # 

DATETIME_FORMAT = '%Y.%m.%d_%H:%M:%S'
RESULT_FILENAME = '/home/pgc/mound_controller.log'

SERIAL_FILENAME_GLOBS = ('/dev/ttyUSB*', '/dev/ttyACM*')
PORT_SPEED = 115200

NL = '\n'.encode('UTF-8')

#PIPE_INLET_SENSOR_ID = '28.ff.0b.f1.92.16.04.86' # Y
#PIPE_MOUND_SENSOR_ID = '28.ff.b5.45.92.16.05.aa' # W - not used
#PIPE_OUTLET_SENSOR_ID = '28.ff.ed.77.45.16.03.f0' # TBD

SENSOR_TO_WATCH_ID = '28.ff.90.86.92.16.05.31' # sensor N for now
# only use WATCHED_SENSOR_SAMPLE when lock is held
WATCHED_SENSOR_SAMPLE_LOCK = threading.Lock()
WATCHED_SENSOR_SAMPLE = PUMP_THRESHOLD_TEMPERATURE

# GPIO port which controls PUMP
PUMP_BCM_PORT = 17

# Arduino devices need some time to recover after the serial port is opened
ARDUINO_RESET_TIME_IN_SECONDS = 3

#
# these routines control the water pump that pushes water through the mound
#

def turn_on_pump():
    GPIO.output(PUMP_BCM_PORT, GPIO.LOW)
    
def turn_off_pump():
    GPIO.output(PUMP_BCM_PORT, GPIO.HIGH)
    
def initialize_pump():
    '''
    initialize the GPIO port and turn off the pump
    
    This uses Broadcom chip numbers, not GPIO numbers
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_BCM_PORT, GPIO.OUT)
    turn_off_pump()

def release_pump():
    '''
    make sure pump is off.
    may eventually do more.
    '''
    turn_off_pump()

    

class writer_thread (threading.Thread):
    '''
    Wait on queue and write/flush each entry that arrives

    Mark ourself as a daemon as we don't have a job when everything else is done
    '''
    def __init__(self, where, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.where = where
        self.queue = queue
        
    def run(self):
        while True:
            data = self.queue.get()
            if data:
                self.where.write(data)
                self.where.flush()
            self.queue.task_done()


def timestamped_event_to_queue(queue, event_text):
    '''
    Put a line of output on the queue to be written to the log
    '''
    when = datetime.datetime.now().strftime(DATETIME_FORMAT)
    result = '{} EVENT {}\n'.format(when, event_text)
    queue.put(result)

def process_sensor_reading(line):
    '''
    Pick apart the data and create a new result to be written.
    
    If this is the sensor we are watching, save a copy of the value for
    others to retrieve.
    '''
    # make sure we update the global value
    global WATCHED_SENSOR_SAMPLE
    
    if len(line.split()) == 3:
        when = datetime.datetime.now().strftime(DATETIME_FORMAT)
        items = line.split()
        result = '{} {} {} {}\n'.format(when, items[0], items[1], items[2])

        # if this is the sensor we are watching, keep a copy others can see
        if items[1] == SENSOR_TO_WATCH_ID:
            if DEBUG:
                print('found ID of "{}" with value of "{}"'.format(items[1], items[2]),
                      file=sys.stderr, flush=True)
            with WATCHED_SENSOR_SAMPLE_LOCK:
                WATCHED_SENSOR_SAMPLE = float(items[2])
            # we can be sure the lock is released here
        return result
    else:
        return None
    
def get_readings_from_port(port):
    '''
    '''
    results = []
    if DEBUG:
        start_time = time.time()
    port.write(NL)  # ask for samples
    
    # read first line returned
    l = port.readline().decode('UTF-8').strip()
    if DEBUG:
        print('line: "{}"'.format(l),
              file=sys.stderr, flush=True)  # don't need a \n
    # process till a blank line is returned
    while len(l.split()) > 0:
        results.append(process_sensor_reading(l))
        l = port.readline().decode('UTF-8')
        if DEBUG:
            print('line:  "{}"'.format(l),
                  file=sys.stderr, flush=True)  # don't need a \n
    if DEBUG:
        print('sample time = {} seconds'.format(time.time() - start_time),
              file=sys.stderr, flush=True)

    return results


class port_reader_thread(threading.Thread):
    '''
    Sample the sensors on a serial port and queue up the 
    results to be written to a persistent place.
    '''
    def __init__(self, queue, port):
        threading.Thread.__init__(self)
        self.daemon = False
        self.queue = queue
        self.port = port
        
    def run(self):
        results = get_readings_from_port(self.port)
        for r in results:
            if r:  # might have a None in the list, if so ignore it
                self.queue.put(r)

class ports_reader_thread(threading.Thread):
    '''
    Periodically sample the sensors on a collection of serial ports and
    queue up the results to be written to a persistent place
    '''
    def __init__(self, queue, ports, interval_in_seconds):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self.ports = ports
        self.interval_in_seconds = interval_in_seconds
        self.keep_running = True
        
    def stop(self):
        self.keep_running = False
        
    def run(self):
        next_sample_time = time.time()
        while self.keep_running:
            threads = []
            for port in self.ports:
                srt = port_reader_thread(write_queue, port)
                threads.append(srt)
                srt.start()
            # wait for everything to complete
            for t in threads:
                t.join()
        
            next_sample_time = next_sample_time + self.interval_in_seconds
            delay_time = next_sample_time - time.time()
            if DEBUG:
                print('ports_reader_thread: delay_time = {}\n'.format(delay_time),
                      file=sys.stderr, flush=True)
        
            if 0 < delay_time:  # don't sleep if already next sample time
                time.sleep(delay_time)


def pump_controller(write_queue, ports, base_interval, pumping_interval):
    '''
    write_queue is where to send output
    
    ports are the port(s) to monitor more frequently when the pump is running
    
    base_interval is how often to sample when the pumps are off
    
    pumping_interval is how often to sample when the pumps are running
    
    
    The pumping algorithm is a loop which does the following:
      Start sampling the watched sensors more frequently
      Start the pump
      Let the water circulate for 30 seconds.
      Each time the watched sensors are read, record the output temperature
      While the temperature is above PUMP_THRESHOLD
        keep pumping
      When the temperature is at or below PUMP_THRESHOLD
        Turn off the pump
        Return the sampling rate of the watched sensors to the monitor rate
        Wait REHEAT_TIME_IN_SECONDS
      Loop back to the top of this sequence 

    '''
    while True:
        # increase sample rate on watched sensors
        timestamped_event_to_queue(write_queue, 'increase_sensor_sampling_rate')
        sensor_thread = ports_reader_thread(write_queue,
                                            ports,
                                            pumping_interval)
        sensor_thread.start() # wait to get some samples

        # get some samples before proceeding
        time.sleep(START_STOP_SECONDS)
        # start the pump
        turn_on_pump()
        timestamped_event_to_queue(write_queue, 'turned_on_pump')
        # let the pump run for 30 second to let temperatures settle
        time.sleep(30)
        
        # when the temperature is low enough set this to False
        keep_going = True
        last_watched_sample = PUMP_THRESHOLD_TEMPERATURE
        while keep_going:
            time.sleep(pumping_interval)
            with WATCHED_SENSOR_SAMPLE_LOCK:
                last_watched_sample = WATCHED_SENSOR_SAMPLE
            if DEBUG:
                print('last_watched_sample:  {}\n'.format(last_watched_sample),
                      file=sys.stderr, flush=True)
                
            if last_watched_sample < PUMP_THRESHOLD_TEMPERATURE:
                keep_going = False
                m = 'last_watched_sample_{}_C'.format(last_watched_sample)
                timestamped_event_to_queue(write_queue, m)

            # we can be sure the lock is released here

        timestamped_event_to_queue(write_queue, 'turning_off_pump')
        turn_off_pump()

        time.sleep(START_STOP_SECONDS) # get some samples before proceeding
        sensor_thread.stop()  # stop the fast sampling
        sensor_thread.join()  # wait for fast sampling to end

        # back to base sample rate while we wait to let the pile re-heat
        timestamped_event_to_queue(write_queue, 'base_sensor_sampling_rate')
        sensor_thread = ports_reader_thread(write_queue,
                                            ports,
                                            base_interval)
        sensor_thread.start()
        timestamped_event_to_queue(write_queue, 'waiting_{}_seconds'.format(REHEAT_TIME_IN_SECONDS))
        time.sleep(REHEAT_TIME_IN_SECONDS)
        sensor_thread.stop()  # stop the base sampling
        sensor_thread.join()  # wait for base sampling to end

        # end of process, run the pump again

#
# main
#
if __name__ == "__main__":

    if SMS:
        # TBD
        twilio_client = twilio_client('SID', 'TOKEN') 
    
    # this will hold the names of serial port devices which might have Arduino
    serial_devices = [] 
    for g in SERIAL_FILENAME_GLOBS:
        serial_devices.extend(glob.glob(g))
    if DEBUG:
        print('available devices include:  {}\n'.format(serial_devices),
              file=sys.stderr, flush=True)

    # get serial port access for each serial device
    ports = set()
    for s in serial_devices:
        ports.add(serial.Serial(s, PORT_SPEED))
    if DEBUG:
        print('ports include:  {}\n'.format(ports),
              file=sys.stderr, flush=True)

    # give the Arduinos time to reset after serial open 
    # as the open process causes the Arduino to reset
    time.sleep(ARDUINO_RESET_TIME_IN_SECONDS)  
    
    # Find the serial port(s) that holds the water pipe sensors
    watched_ports = set()
    for p in ports:
        if DEBUG:
            print('reading port {}:\n'.format(p) ,
                  file=sys.stderr, flush=True)
        results = get_readings_from_port(p)
        for r in results:
#             if PIPE_OUTLET_SENSOR_ID in r:
#                 watched_ports.add(p)
#                 break
#             if PIPE_INLET_SENSOR_ID in r:
#                 watched_ports.add(p)
#                 break
#             if PIPE_MOUND_SENSOR_ID in r:
#                 watched_ports.add(p)
#                 break
            if SENSOR_TO_WATCH_ID in r:
                watched_ports.add(p)
                break

    # Now make the set of ports that do not have the pipe sensors
    monitored_ports = set()
    for p in ports:
        if p not in watched_ports:
            monitored_ports.add(p)
    
    if DEBUG:
        print('watched port(s): {}\n'.format(watched_ports),
              file=sys.stderr, flush=True)
        print('monitored port(s): {}\n'.format(monitored_ports),
              file=sys.stderr, flush=True)


    data_file_name = RESULT_FILENAME
    with open(data_file_name, 'a') as output_file:
        # set up queue to handle output to single place between many threads
        write_queue = queue.Queue(30)
        writer = writer_thread(output_file, write_queue)
        writer.start()

        # set up the GPIO port and turn off the pump
        initialize_pump()

        # ready to go, log what is happening
        timestamped_event_to_queue(write_queue, 'starting_controller')

        # two things to do:  
        #    Daemon thread to monitor sensors in the mound which are not in the water
        #    thread to control the states of the pump and overall system

        if DEBUG:
            print('starting backgroud sensors\n',
                  file=sys.stderr, flush=True)
        background_sensor_thread = ports_reader_thread(write_queue,
                                                       monitored_ports,
                                                       BASE_SAMPLE_INTERVAL_IN_SECONDS)
        background_sensor_thread.start()

        if DEBUG:
            print('waiting to let monitors get started ...\n',
                  file=sys.stderr, flush=True)
        time.sleep((BASE_SAMPLE_INTERVAL_IN_SECONDS * 2) + 5)
        
        if DEBUG:
            print('starting pump controller\n',
                  file=sys.stderr, flush=True)
        
        pump_controller(write_queue, watched_ports, 
                        BASE_SAMPLE_INTERVAL_IN_SECONDS, 
                        PUMPING_SAMPLE_INTERVAL_IN_SECONDS)
        if DEBUG:
            print('back from pump controller\n',
                  file=sys.stderr, flush=True)
        
        # clean up if we ever get here
        background_sensor_thread.stop()
        # ensure any remaining data has been written after stop
        write_queue.join()
        # leave pump turned off
        release_pump()
