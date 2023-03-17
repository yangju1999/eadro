# 数据集下载、压缩后放到 codes/preprocess/data_set/
# 数据集中,faults记录中的nginx-thrift 应该是笔误，实际应该叫 nginx-web-server
# 日志数据使用logparser 项目中的drain算法处理
## 运行align.py和main.py时需要指定应用名称，这里默认写死叫 try
所以 codes/chunks目录下是try，codes/preprocess/parsed_data 目录下也是try

# 数据处理

## 数据集下载、压缩后放到 codes/preprocess/data_set/
我用的是sn数据，所以是  codes/preprocess/data_set/sn/xxx
## records 故障注入记录数据处理
根目录运行 sh parse.sh
## 日志数据处理
直接根目录，运行 sh parse_logs.sh

以下内容是对脚本处理的说明
cd codes/preprocess
### pre_parse_logs.py
将数据中的日志文件，按照 <service> <timestamp> <Content> 格式清洗出来

python pre_parse_logs.py

### drain_sn.py
用drain算法，从日志数据中提取出事件

python drain_sn.py

### parse_log.py
从 日志事件中提取事件名称，做成词典，将日志csv列名调整一下

python parse_log.py

### 挪动处理后的日志csv

使用shell 脚本，或者其他方法，按时间顺序，将codes/preprocess/data_set/sn/data/Drain_sn_result/*/logs.csv
复制到 codes/preprocess/parsed_data/try 目录下，分别叫logs0.csv,logs1.csv,logs2.csv,logs3.csv

再复制 codes/preprocess/data_set/sn/data/Drain_sn_result/templates.json
到 codes/preprocess/parsed_data/try 目录下

## trace数据处理

直接在根目录运行 sh parse_trace.sh 即可

以下内容是对脚本处理的说明
### parse_trace.py
从指定trace文件中，提取出服务调用关系和耗时数据


## metrics数据处理

sh parse_metrics.sh