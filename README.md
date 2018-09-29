# MoundController
Control a compost pile used to generate hot water

The Data is from a large compost pile which dumps the heat in to a pool.


### Changes

##### 2017.11.15
Disconnected pump as part fo the pool winterization process.

##### September 2018:  Moved to "Phase 2" of Project

* Saved old data in "*phase1" directories

* New Pump Algorithm:
    The pumping algorithm is a loop which does the following:
    * Start the pump (and faster samples on watched sensors)
    * Let the water circulate for MINIMUM_PUMP_TIME_IN_SECONDS .
    * Each time the watched sensors are read, record the output temperature
    * While the temperature is above PUMP_THRESHOLD
        * keep pumping
    * When the temperature is at or below PUMP_THRESHOLD
        * Turn off the pump
        * Return the sampling rate of the watched sensors to the monitor rate
        * Wait REHEAT_TIME_IN_SECONDS
    * Loop back to the top of this sequence 
    
* Problems with current pipe sensors.  For now:
    * Inlet is sensor Y
    * Outlet is sensor TBD (broken)
    * pipe sensor W is just hanging out in the air -- will put in pipe at outlet

* Relay for pump is broken.  
    * Moved from first to second relay (on 4 relay card).
    * This only involves moving wires, the code still uses GPIO 17.

##### Source code is now in github
* Documents algorithm details to go with collected data.
* Perhaps someone will find this useful.  

##### 2018 Sept 29:  Addressed outlet sensor issue (described above)
* Added outlet temperature sensor (sensor W) in to pipe a couple meters after it exits the mound.
* Changed control SW to use this sensor to make pump decisions and set threshold to 50 degrees C.
