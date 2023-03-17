#/bin/bash
# prepare data
#sh parse.sh
#sh parse_logs.sh
#sh parse_metrics.sh
#sh parse_trace.sh
# prepare data align
cd codes/preprocess
python align.py --name try
# training!
cd ..
python main.py --data try