import json
import sys
import argparse
def main():
    '''
    从故障注入记录文件（例如 SN.fault-2022-04-17T181245D2022-04-17T183616.json）
    整理出故障时间，方便后面给数据打label（故障注入的时间，就是要判断出故障的时间）
    Returns:

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--source")
    parser.add_argument("--target")
    params = vars(parser.parse_args())
    print(params)
    fp = open(params["source"],'rb')
    data = json.load(fp)
    # 时间单位用秒，直接四舍五入，统一成int
    result = {'start':int(data['start']),'end':int(data['end']),'faults':[]}
    for item in data['faults']:
       result['faults'].append( {
           'service':'-'.join(item['name'].split('-')[1:-1]),
           's':int(item['start']),
           'e':int((item['start']+item['duration'])),
       })
    out_fp = open(params['target'],'w')
    json.dump(result,out_fp)
main()