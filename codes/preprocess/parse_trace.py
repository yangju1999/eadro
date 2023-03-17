import json
import sys
import argparse


def get_parent_service_name(parent_span_id,spans,names):
    for span in spans:
        if span['spanID'] != parent_span_id:
            continue
        return get_service_name(span,names)


def get_service_name(span,names):
    if span['processID']:
        return names[span['processID']]
    return ''


def find_call(span,spans,names):
    # self parent
    if len(span['references']) == 0:
        serviceName = get_service_name(span,names)
        return True,serviceName,serviceName
    if len(span['references'])>0 and span['references'][0]['refType'] == 'CHILD_OF':
        serviceName = get_service_name(span,names)
        parentServiceName = get_parent_service_name(span['references'][0]['spanID'],spans,names)
        return True,parentServiceName,serviceName
    return False,"",""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source")
    parser.add_argument("--target")
    params = vars(parser.parse_args())
    print(params)
    fp = open(params["source"],'rb')
    data = json.load(fp)
    result = {}
    apiList = ['social-graph-service', 'compose-post-service', 'post-storage-service', 'user-timeline-service',
               'url-shorten-service', 'user-service',
               'media-service', 'text-service', 'unique-id-service', 'user-mention-service', 'home-timeline-service',
               "nginx-web-server"]
    service2id = {s:idx for idx, s in enumerate(apiList)}
    for item in data:
        names = {}
        processes = item['processes']
        # 抽取service name 与process id
        for process in processes:
            names[process] = processes[process]['serviceName']
        spans = item['spans']
        for span in spans:
            is_call = False
            is_call,parent_service_name,service_name = find_call(span,spans,names)
            if not is_call:
                continue
            curTime =  str(int(span['startTime']/1e6))
            if parent_service_name is None:
                continue
            call = "%d-%d" % (service2id[parent_service_name],service2id[service_name])
            if curTime not in result:
                result[curTime] = {}
            if call not in result[curTime]:
                result[curTime][call] = []
            result[curTime][call].append(span['duration'])
    out_fp = open(params['target'],'w')
    json.dump(result,out_fp)
main()
