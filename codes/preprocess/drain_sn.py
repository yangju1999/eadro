import sys
sys.path.append('../')
from logparser import Drain

input_dir  = 'data_set/sn/data/'  # The input directory of log file
output_dir = 'data_set/sn/data/Drain_sn_result/'  # The output directory of parsing results
#log_file   = 'SN.2022-04-17T181245D2022-04-17T183616/logs.json.parsed.txt'  # The input log file name
log_format = '<service> <timestamp> <Content>'  # cui_2k log format
# Regular expression list for optional preprocessing (default: [])
regex      = [
    r'(?<=")[0-9a-zA-Z]+[-_]{1,}[0-9a-zA-Z-_]+(?=")', # numbers-char-_
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+\.*\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]
st         = 0.5  # Similarity threshold
depth      = 4  # Depth of all leaf nodes
log_files = [
    'SN.2022-04-17T181245D2022-04-17T183616/logs.json.parsed.txt', # The input log file name
    'SN.2022-04-17T190213D2022-04-17T192544/logs.json.parsed.txt', # The input log file name
    'SN.2022-04-17T183729D2022-04-17T190100/logs.json.parsed.txt', # The input log file name
    'SN.2022-04-17T192658D2022-04-17T195031/logs.json.parsed.txt', # The input log file name
]
for log_file in log_files:
    parser = Drain.LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, rex=regex)
    parser.parse(log_file)