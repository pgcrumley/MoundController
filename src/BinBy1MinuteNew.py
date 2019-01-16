#!env python3
"""
MIT License

Copyright (c) 2017, 2019 Paul G Crumley

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


read in the data.  for each element:
-- add the sensor id to a set of sensor ids
-- make a map with keys of each hour seen and in each key (hour) there will
be a map with keys of the sensor id and for each sensor id there will be a 
list of values seen in that hour.
-- make a set of all hours seen

After reading in everything:
-- make a sorted list of the hours
-- make a sorted list of the ids
-- After this is created a new map with keys of each hour will be made which 
has a map by sensor id which holds the average temperature for that id for that 
hour.

Then make a list of tuples of (hour, id, average temperature)
sort this by hour.
"""

import sys
import SensorIdToName

DEBUG = 0

class SensorValue():
    def __init__(self):
        self.count = 0
        self.sum = 0.0
        
    def addValue(self, value):
        self.count = self.count + 1
        self.sum = self.sum + float(value)
        
    def getAverage(self):
        return (self.sum / self.count)
    
    def getCount(self):
        return self.count

    
sensor_map_values_by_timestamp = dict()

timestamp_set = set()
name_set = set()
    



if __name__ == "__main__":

    if (2 == len(sys.argv)) and ('-' == sys.argv[1]):
        ifile=sys.stdin
        ofile=sys.stdout
    else:
        ifile = open('../Data/temp.log')
        ofile = open('../Data/temp_1m.csv', 'w')

    entries = 0
    for line in ifile:
        line = line.translate(dict.fromkeys([0]))  # remove null characters
        sl = line.split()
        if len(sl) != 3 and len(sl) != 3:
            print('line {} is "{}"'.format(entries+1, sl), file=sys.stderr)
            continue
        timestamp = sl[0]
        name = sl[1]
        temperature = sl[2]
        if not timestamp.startswith( ('2017', '2018', '2019') ):
            print('line {} is "{}"'.format(entries+1, sl), file=sys.stderr)
            continue

        #                     111111111
        #           0123456789012345678
        # format is yyyy.mm.dd_hh.mm.ss
        # we only want by minute so toss all to the right
        timestamp = timestamp[0:16]  # toss second parts

        # keep track of all the unique ids & timestampe
        timestamp_set.add(timestamp)
        name_set.add(name)
        
        # if there is no entry for this minute, make one 
        if timestamp not in sensor_map_values_by_timestamp:
            sensor_map_values_by_timestamp[timestamp] = dict()
        if name not in sensor_map_values_by_timestamp[timestamp]:
            sensor_map_values_by_timestamp[timestamp][name] = SensorValue()
        sensor_map_values_by_timestamp[timestamp][name].addValue(temperature)
        entries+=1

    if DEBUG:            
        print('{} entries read'.format(entries))
        print(len(name_set))
        print(name_set)
        print(len(timestamp_set))
        print(timestamp_set)
        tsk = sensor_map_values_by_timestamp.keys()
        print(len(tsk))
        print(tsk)
        print('')
        
    stsk = sorted(list(timestamp_set))
    sn = sorted(list(name_set))
    
    # print the heading line
    print('"{}"'.format('when'), file=ofile, end='')
    for n in sn:
        print(',"{}"'.format(n), file=ofile, end='')
    print('\n', file=ofile, end='')
    # print data
    for ts in stsk:
        print('"{}"'.format(ts), file=ofile, end='')
        for n in sn:
            if n in sensor_map_values_by_timestamp[ts]:
                print(',{:.4f} '.format(sensor_map_values_by_timestamp[ts][n].getAverage()), file=ofile, end='')
            else:
                print(', ', file=ofile, end='')
        print('\n', file=ofile, end='')
    # print(sensor_map_values_by_timestamp)
