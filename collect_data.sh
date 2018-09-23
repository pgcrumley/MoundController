#!/bin/bash
#
# MIT License
# 
# Copyright (c) 2017, 2018 Paul G Crumley
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @author: pgcrumley@gmail.com
#
echo pulling from git to make sure up-to-date ...
#
git pull
echo done


#
echo getting files from mound ...
#
mkdir -p mound
cd mound
rsync -zv 'pgc@192.168.1.220:/home/pgc/*temper*' .
rsync -zv 'pgc@192.168.1.220:/home/pgc/mound*' .
cd ..
echo done

#
echo creating merged temperature data ...
#
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

#
echo binning data ...
#
../src/BinByDayNew.py - < temp.log > temp_1d.csv &
../src/BinByHourNew.py - < temp.log > temp_1h.csv &
../src/BinBy10MinutesNew.py - < temp.log > temp_10m.csv &
../src/BinBy1MinuteNew.py - < temp.log > temp_1m.csv &
wait
echo done binning data

# move back to top from work directory
cd ..

#
echo moving logs to data staging area ...
#
cp work/temp_*.csv Data
cp work/event.log Data

#zip Data/temp_data.zip temp_1d.csv temp_1h.csv temp_10m.csv temp_1m.csv
#zip Data/event_data.zip event.log
#zip Data/log.zip full.log
#grep '^2017.12' full.log > Data/2017.12.log
#grep '^2018.01' full.log > Data/2018.01.log
#grep '^2018.06' full.log > Data/2018.06.log
#grep '^2018.07' full.log > Data/2018.07.log


#
echo uploading data to git ...
#
git add -f Data/*
git commit -m "update data on `date`"
git push

echo done saving result to git
