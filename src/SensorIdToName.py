#!/usr/bin/python3
"""
MIT License

Copyright (c) 2017 Paul G Crumley

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


Given a sensor type and id, return a name.

"""


name_from_type_and_id_map = {
    'DS18B20' : {
        '28.ff.b5.45.92.16.05.aa' : 'pipe_outlet', # W
        '28.ff.ed.77.45.16.03.f0' : 'pipe_outlet_old', 
        '28.ff.0b.f1.92.16.04.86' : 'pipe_inlet', # Y
        '28.ff.1d.8c.50.16.04.4f' : 'sensor_A',  # was pipe_East
        '28.ff.a6.e8.92.16.04.f2' : 'sensor_F',
        '28.ff.7c.e5.92.16.04.8c' : 'sensor_G',
        '28.ff.81.51.00.16.01.01' : 'sensor_H',
        '28.ff.25.95.55.16.03.e8' : 'sensor_I',
        '28.ff.88.45.92.16.05.c2' : 'sensor_K',
        '28.ff.d7.39.93.16.04.77' : 'sensor_L',
        '28.ff.59.89.92.16.05.7a' : 'sensor_M', # broken, retired
        '28.ff.e2.42.92.16.05.e8' : 'sensor_M', # id of replacement M
        '28.ff.90.86.92.16.05.31' : 'sensor_N',
        '28.ff.ce.83.92.16.05.87' : 'sensor_O',
        '28.ff.d0.49.92.16.05.7b' : 'sensor_P',  # broken, retired
        '28.ff.c7.54.90.16.05.bc' : 'sensor_Q',
        '28.ff.2b.f7.92.16.04.77' : 'sensor_R',
        '28.ff.12.67.90.16.05.f0' : 'sensor_S',  # broken, retired
        '28.ff.cf.f3.92.16.04.bc' : 'sensor_T',  # broken, retired
        '28.ff.45.43.92.16.05.05' : 'sensor_T',  # id of replacement T
        '28.ff.ee.48.92.16.05.d2' : 'sensor_U',
        '28.ff.25.6a.90.16.05.b8' : 'sensor_V',
        '28.ff.73.58.90.16.05.fe' : 'sensor_X',
        '28.ff.13.84.92.16.05.b3' : 'sensor_Z',
        '28.ff.6d.b0.00.16.02.de' : 'monitor_ambient_1',
        '28.ff.77.a9.00.16.02.b4' : 'monitor_ambient_2',
        '28.ff.e2.2b.55.16.03.1f' : 'pool_water_return',
        '28.ff.03.9f.51.16.04.8a' : 'pool_water_return_ambient',
        '28.ff.37.29.92.16.05.60' : 'TBD_sensor_B',
        '28.ff.de.37.93.16.04.91' : 'TBD_sensor_C',
        '28.ff.0a.25.92.16.05.1a' : 'TBD_sensor_D',
        '28.ff.ec.f6.92.16.04.8b' : 'TBD_sensor_E',
        '28.ff.a7.e8.92.16.04.3f' : 'TBD_sensor_J',
        '28.ff.ad.4c.92.16.05.7b' : 'TBD_sensor_AA',
        '28.ff.6d.23.92.16.05.53' : 'TBD_sensor_AB',
        '28.ff.a2.ef.92.16.04.6b' : 'TBD_sensor_CD',
        '28.ff.c0.83.92.16.05.25' : 'TBD_sensor_EF',
        '28.ff.65.fd.92.16.04.27' : 'TBD_sensor_GH',
        },
    'BME280' : {
        '000000005eb857ba' : 'attic', 
        '000000005c42c396' : 'living_room',
        '00000000e013dbae' : 'north_ambient',
        '00000000f0d72ad2' : 'north_crawl_space',
        '00000000fcf52270' : 'rec_room', 
        '0478d0c8e17b84a9bcef9c32c38d2a07' : 'rec_room',  
        'cde66edd76c727af62dee27071cb76b4' : 'living_room',  
        'ed8828854b0f744b76125be990c8f7d2' : 'attic',
        'ee55c8aaea4ead890272e7b3896f1e58' : 'north_crawl_space'
        },
    'Si7021' : {
        '00000000ea2582d5' : 'rec-room'
        } 
                             }

def name_from_type_and_id(type, id):
    '''
    if known, return the name for the sensor of the type / id pair.
    
    if not known, return a fabricated string with the type and id.
    '''
    if type in name_from_type_and_id_map:
        if id in name_from_type_and_id_map[type]:
            return name_from_type_and_id_map[type][id]
    # no name -- return fabricated string
    return 'no_name_for_{}_{}'.format(type, id)



name_to_color_map = {
        'pipe_inlet' : 'lightblue',
        'pipe_East' : 'aqua',
        'pipe_West' : 'aquamarine',
        'pipe_outlet' : 'navy',
        'sensor_F' : 'magenta',
        'sensor_G' : 'lime',
        'sensor_I' : 'tan',
        'sensor_K' : 'olive',
        'sensor_L' : 'orange',
        'sensor_M' : 'plum',
        'sensor_N' : 'salmon',
        'sensor_O' : 'red',
        'sensor_P' : 'pink',
        'sensor_Q' : 'orchid',
        'sensor_R' : 'indigo',
        'sensor_S' : 'goldenrod',
        'sensor_T' : 'darkgreen',
        'sensor_U' : 'coral',
        'sensor_V' : 'crimson',
        'sensor_X' : 'brown',
        'sensor_Z' : 'green',
        'monitor_ambient_1' : 'yellow',
        'monitor_ambient_2' : 'beige',
        'pool_water_return' : 'blue'}


def name_to_color(name):
    '''
    if known, return the color for name otherwise return 'black'
    '''
    if name in name_to_color_map:
        return name_to_color_map[name]
    else:
        return 'black'

# 
# if invoked as a program dump out all the info
#
if __name__ == '__main__':
    for type in name_from_type_and_id_map.keys():
        print('{}:'.format(type))
        for id in name_from_type_and_id_map[type].keys():
            print('  {} : "{}"'.format(id, name_from_type_and_id_map[type][id]))

    exit()
    print(name_from_type_and_id('BME280', '000000005eb857ba'))
    print(name_from_type_and_id('BME280', '0'))
    print(name_from_type_and_id('DS18B20', '28.ff.e2.2b.55.16.03.1f'))
    print(name_from_type_and_id('DS18B20a', '28.ff.e2.2b.55.16.03.1f'))
    
    
