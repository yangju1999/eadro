import json
from datetime import datetime

def format(row):
    #dt [2022-Apr-17 10:12:50.490796]
    tmp = row.split(" ")
    dt = " ".join(tmp[0:2])
    ts = int(datetime.strptime(dt,"[%Y-%b-%d %H:%M:%S.%f]").timestamp())
    return str(ts)+" "+ ' '.join(tmp[2:])


def parse(log):
    lines = []
    fp = open(log,'rb')
    data = json.load(fp)
    for service,rows in data.items():
        for row in rows:
            line = service + " " + format(row)
            lines.append(line)
    return lines


def save(lines,log):
    fp = open(log+'.parsed.txt','w')
    fp.write('\n'.join(lines))


def main():
    logs = [
        "data_set/sn/data/SN.2022-04-17T181245D2022-04-17T183616/logs.json",
        "data_set/sn/data/SN.2022-04-17T183729D2022-04-17T190100/logs.json",
        "data_set/sn/data/SN.2022-04-17T190213D2022-04-17T192544/logs.json",
        "data_set/sn/data/SN.2022-04-17T192658D2022-04-17T195031/logs.json",
    ]
    for log in logs:
        lines = parse(log)
        save(lines,log)

main()