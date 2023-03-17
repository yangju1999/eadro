#!/bin/bash
sysname="try"
mkdir -p ./codes/preprocess/parsed_data/$sysname
python codes/preprocess/parse.py --source=codes/preprocess/data_set/sn/data/SN.fault-2022-04-17T181245D2022-04-17T183616.json --target=./codes/preprocess/parsed_data/$sysname/records0.json
python codes/preprocess/parse.py --source=codes/preprocess/data_set/sn/data/SN.fault-2022-04-17T183729D2022-04-17T190100.json --target=./codes/preprocess/parsed_data/$sysname/records1.json
python codes/preprocess/parse.py --source=codes/preprocess/data_set/sn/data/SN.fault-2022-04-17T190213D2022-04-17T192544.json --target=./codes/preprocess/parsed_data/$sysname/records2.json
python codes/preprocess/parse.py --source=codes/preprocess/data_set/sn/data/SN.fault-2022-04-17T192658D2022-04-17T195031.json --target=./codes/preprocess/parsed_data/$sysname/records3.json
