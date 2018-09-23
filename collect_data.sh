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

#echo getting files from pool...
#mkdir -p pool
#cd pool
#rsync -zv 'pgc@192.168.1.210:/home/pgc/*temper*' .
#cd ..
#echo done


echo creating merged temperature data
mkdir -p work
cd work
# mv temp.log temp.log.old
cat ../mound/* |\
  tr -d '\000' |\
  sort |\
  sed -f ../src/SensorIdToName.sed > full.log
#
# full.log now has all the data with names rather than IDs and no NULLS
#
grep EVENT full.log > event.log &
grep -v EVENT full.log > temp.log &
wait
echo full.log, event.log and temp.log are ready to use

echo binning data...
mv temp_1d.csv temp_1d.csv.old
mv temp_1h.csv temp_1h.csv.old
mv temp_10m.csv temp_10m.csv.old
mv temp_1m.csv temp_1m.csv.old
../src/BinByDayNew.py - < temp.log > temp_1d.csv &
../src/BinByHourNew.py - < temp.log > temp_1h.csv &
../src/BinBy10MinutesNew.py - < temp.log > temp_10m.csv &
../src/BinBy1MinuteNew.py - < temp.log > temp_1m.csv &
wait
echo done binning data

cd ..
echo back in `pwd`

echo uploading data...

cp work/temp_*.csv Data
cp work/event.log Data

#zip Data/temp_data.zip temp_1d.csv temp_1h.csv temp_10m.csv temp_1m.csv
#zip Data/event_data.zip event.log
#zip Data/log.zip full.log

#grep '^2017.12' full.log > Data/2017.12.log
#grep '^2018.01' full.log > Data/2018.01.log
#grep '^2018.06' full.log > Data/2018.06.log
#grep '^2018.07' full.log > Data/2018.07.log


git add -f Data/*
git commit -m "update data on `date`"


git push
echo done saving result to git
