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

Run as root and cycle pump on and off every 15 seconds to test the circuit

"""

import sys
import time

import RPi.GPIO as GPIO

DEBUG = 1

# GPIO port which controls PUMP
PUMP_BCM_PORT = 17


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

    
#
# main
#
if __name__ == "__main__":

    # set up the GPIO port and turn off the pump
    initialize_pump()
    print('initialized pump',
              file=sys.stderr, flush=True)

    try:
        while True:
            turn_on_pump()
            print('turned on pump',
                  file=sys.stderr, flush=True)
            time.sleep(15)
            turn_off_pump()
            print('turned off pump',
                  file=sys.stderr, flush=True)
            time.sleep(15)
    except Exception as e:
        print('caught "{}"'.format(e),
              file=sys.stderr, flush=True)

    # leave pump turned off
    print('released pump',
              file=sys.stderr, flush=True)
    release_pump()
    print('exited',
              file=sys.stderr, flush=True)
