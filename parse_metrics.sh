#!/bin/bash
cd codes/preprocess

for f in data_set/sn/data/SN.2022-04-17T181245D2022-04-17T183616/metrics/*.csv; do
  #echo $f
  t=`basename "$f"`
  echo $t
  mkdir -p ./parsed_data/try/metrics0
  cp "$f" ./parsed_data/try/metrics0/
done
for f in data_set/sn/data/SN.2022-04-17T183729D2022-04-17T190100/metrics/*.csv; do
  #echo $f
  t=`basename "$f"`
  echo $t
  mkdir -p ./parsed_data/try/metrics1
  cp "$f" ./parsed_data/try/metrics1/
done
for f in data_set/sn/data/SN.2022-04-17T190213D2022-04-17T192544/metrics/*.csv; do
  #echo $f
  t=`basename "$f"`
  echo $t
  mkdir -p ./parsed_data/try/metrics2
  cp "$f" ./parsed_data/try/metrics2/
done
for f in data_set/sn/data/SN.2022-04-17T192658D2022-04-17T195031/metrics/*.csv; do
  #echo $f
  t=`basename "$f"`
  echo $t
  mkdir -p ./parsed_data/try/metrics3
  cp "$f" ./parsed_data/try/metrics3/
done
