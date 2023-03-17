#!/bin/bash

cd codes/preprocess
python pre_parse_logs.py
python drain_sn.py
python parse_log.py
# 用logparser项目代码处理的日志文件
cp data_set/sn/data/Drain_sn_result/SN.2022-04-17T181245D2022-04-17T183616/logs.csv ./parsed_data/try/logs0.csv
cp data_set/sn/data/Drain_sn_result/SN.2022-04-17T183729D2022-04-17T190100/logs.csv ./parsed_data/try/logs1.csv
cp data_set/sn/data/Drain_sn_result/SN.2022-04-17T190213D2022-04-17T192544/logs.csv ./parsed_data/try/logs2.csv
cp data_set/sn/data/Drain_sn_result/SN.2022-04-17T192658D2022-04-17T195031/logs.csv ./parsed_data/try/logs3.csv
cp data_set/sn/data/Drain_sn_result/templates.json ./parsed_data/try/
