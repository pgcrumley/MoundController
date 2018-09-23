#!/bin/bash

echo pulling data...
git pull
echo done


echo getting files from mound...
mkdir -p mound
cd mound
rsync -zv 'pgc@192.168.1.220:/home/pgc/*temper*' .
rsync -zv 'pgc@192.168.1.220:/home/pgc/mound*' .
cd ..
echo done

echo getting files from pool...
mkdir -p pool
cd pool
rsync -zv 'pgc@192.168.1.210:/home/pgc/*temper*' .
cd ..
echo done


echo creating merged temperature data
# mv temp.log temp.log.old
cat mound/* pool/* | tr -d '\000' | sort > cleaned.log
sed -f src/SensorIdToName.sed < cleaned.log > full.log &
grep EVENT cleaned.log > event.log &
grep -v EVENT cleaned.log | sed -f src/SensorIdToName.sed > temp.log
echo done 

echo binning data...
mv temp_1d.csv temp_1d.csv.old
mv temp_1h.csv temp_1h.csv.old
mv temp_10m.csv temp_10m.csv.old
mv temp_1m.csv temp_1m.csv.old
src/BinByDayNew.py - < temp.log > temp_1d.csv &
src/BinByHourNew.py - < temp.log > temp_1h.csv &
src/BinBy10MinutesNew.py - < temp.log > temp_10m.csv &
src/BinBy1MinuteNew.py - < temp.log > temp_1m.csv &
wait
echo done

echo uploading data...
#cp temp_1d.csv Data
#cp temp_1h.csv Data
#cp temp_10m.csv Data
#cp temp_1m.csv Data
#cp event.log Data
zip Data/temp_data.zip temp_1d.csv temp_1h.csv temp_10m.csv temp_1m.csv
zip Data/event_data.zip event.log
zip Data/log.zip full.log

#grep '^2017.12' full.log > Data/2017.12.log
#grep '^2018.01' full.log > Data/2018.01.log
grep '^2018.06' full.log > Data/2018.06.log
grep '^2018.07' full.log > Data/2018.07.log
git add -f Data/*
git commit -m 'update data'
git push
echo done
