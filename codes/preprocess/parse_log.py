
import pandas as pd
import json


def unique(l):
    return list(set(l))


def parse(dir):
    input = dir + "logs.json.parsed.txt_structured.csv"
    output = dir + "logs.csv"
    df = pd.read_csv(input)
    df_new = df[['service', 'timestamp', 'EventId']]
    df_out = df_new.rename(columns={'EventId': 'event'})
    df_out.to_csv(output)


def parse_tpl(folders, out_file):
    events = []
    for folder in folders:
        input = folder + "logs.json.parsed.txt_templates.csv"
        df = pd.read_csv(input)
        for event in df['EventId']:
            events.append(event)

    fp = open(out_file, 'w')
    json.dump(unique(events), fp)


def main():
    folders = [
        "data_set/sn/data/Drain_sn_result/SN.2022-04-17T181245D2022-04-17T183616/",
        "data_set/sn/data/Drain_sn_result/SN.2022-04-17T183729D2022-04-17T190100/",
        "data_set/sn/data/Drain_sn_result/SN.2022-04-17T190213D2022-04-17T192544/",
        "data_set/sn/data/Drain_sn_result/SN.2022-04-17T192658D2022-04-17T195031/",
    ]
    out_file = "data_set/sn/data/Drain_sn_result/templates.json"
    for folder in folders:
        parse(folder)
    parse_tpl(folders, out_file)


main()