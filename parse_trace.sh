#!/bin/bash
cd codes/preprocess
python parse_trace.py --source='data_set/sn/data/SN.2022-04-17T181245D2022-04-17T183616/spans.json' --target=./parsed_data/try/traces0.json
python parse_trace.py --source='data_set/sn/data/SN.2022-04-17T183729D2022-04-17T190100/spans.json' --target=./parsed_data/try/traces1.json
python parse_trace.py --source='data_set/sn/data/SN.2022-04-17T190213D2022-04-17T192544/spans.json' --target=./parsed_data/try/traces2.json
python parse_trace.py --source='data_set/sn/data/SN.2022-04-17T192658D2022-04-17T195031/spans.json' --target=./parsed_data/try/traces3.json
