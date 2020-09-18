#!/usr/bin/env python3
# coding:utf-8
import sys
import requests
import json
import time
#键入企业微信相关信息
CorpID = ''
CorpSecret = ''
AgentID=1

def SendCardMessageToApp(UserId,Subject,Content,task_id):

    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])

    rawdata = {
   "touser" : UserId,
   "msgtype" : "taskcard",
   "agentid" : AgentID,
    "taskcard" : {
            "title" : Subject,
            "description" : Content,
            "task_id":task_id,
			"btn":[
                {
                    "key": "ack",
                    "name": "确认开始处理",
                    "replace_name": "确认开始处理",
                    "color":"red"
                },
                {
                    "key": "close",
                    "name": "关闭问题",
                    "replace_name": "已关闭问题"
                }
            ]

   },
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}


    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    print(PostContent.json())
    print(rawdata)

    return 1

def SendMarkDownToApp(UserId,Content):

    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])

    rawdata = {
   "touser" : UserId,
   "msgtype" : "markdown",
   "agentid" : AgentID,
    "markdown" : {
        "content":Content

    },
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}


    #print(json.dumps(rawdata))
    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    print(PostContent.json())
    print(rawdata)

    return 1


if __name__ == '__main__':
    proxy = {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'}
    UserId = sys.argv[1]
    UserId=UserId.replace(' ','')
    Subject = sys.argv[2]
    Message = sys.argv[3]

    FormedArray = Message.split('@@@')


    if Subject.find('故障发生')>-1:
        EventID = FormedArray[6]
        Random = int(round(time.time() * 1000))
        task_id = str(str(EventID) + "@" + str(Random))
        FormedArray[0] = "发生时间：" + FormedArray[0] + ' '
        FormedArray[1] = "on " + FormedArray[1] + '\n'
        FormedArray[2] = "故障名：" + FormedArray[2] + '\n'
        FormedArray[3] = "<div class=\"highlight\">主机名：" + FormedArray[3] + '</div>'
        FormedArray[4] = "<div class=\"highlight\">主机IP:" + FormedArray[4] + '</div>'
        FormedArray[5] = "<div class=\"highlight\">故障等级:" + FormedArray[5] + '</div>\n'
        FormedArray[6] = "<div class=\"gray\">Original problem ID：" + FormedArray[6] + '</div>'
        Content = ''
        for data in FormedArray:
            Content = Content + data

        SendCardMessageToApp(UserId, Subject, Content, task_id)
        with open('/tmp/access.log', 'a') as f:
            f.write('满足故障发生\n')
    elif Subject.find('故障更新')>-1:
        UpdateTime=FormedArray[0]
        UpdateDate=FormedArray[1]
        ProblemName=FormedArray[2]
        HostName=FormedArray[3]
        HostIP=FormedArray[4]
        ProblemSev=FormedArray[5]
        UpdateUser=FormedArray[6]
        UpdateContent=FormedArray[7]
        IsAck=FormedArray[8]
        ProblemID=FormedArray[9]
        Content='<font color=\"info\">故障更新</font>\n>更新时间：<font color=\"comment\">'+UpdateTime+' on '+UpdateDate+'</font>\n>故障名：<font color=\"warning\">'+ProblemName+'</font>\n>主机名：<font color=\"comment\">'+\
        HostName+'</font>\n>主机IP: <font color=\"comment\">'+HostIP+'</font>\n>故障等级: <font color=\"comment\">'+ProblemSev+'</font>\n>更新者: <font color=\"info\">'+UpdateUser+\
            '</font>\n>更新内容: <font color=\"info\">'+UpdateContent+'</font>\n>是否ACK: <font color=\"warning\">'+IsAck+'</font>\n>Original problem ID：<font color=\"comment\">'+ProblemID+'</font>'
        SendMarkDownToApp(UserId, Content)
        with open('/tmp/access.log', 'a') as f:
            f.write('满足故障更新\n')

    elif Subject.find('故障解决')>-1:
        ResolveTime=FormedArray[0]
        ResolveDate=FormedArray[1]
        ProblemName=FormedArray[2]
        HostName=FormedArray[3]
        HostIP=FormedArray[4]
        ProblemSev=FormedArray[5]
        ProblemID=FormedArray[6]
        Content='<font color=\"info\">故障解决</font>\n>解决时间：<font color=\"info\">'+ResolveTime+' on '+ResolveDate+'</font>\n>故障名：<font color=\"info\">'+ProblemName+'</font>\n>主机名：<font color=\"info\">'+\
            HostName+'</font>\n>主机IP: <font color=\"info\">'+HostIP+'</font>\n>故障等级: <font color=\"info\">'+ProblemSev+'</font>\n>Original problem ID：<font color=\"info\">'+ProblemID+'</font>'
        SendMarkDownToApp(UserId, Content)
        with open('/tmp/access.log', 'a') as f:
            f.write('满足故障解决\n')
    else:
        with open('/tmp/access.log', 'a') as f:
            f.write('无满足\n')

    with open('/tmp/access.log','a') as f:
        for info in FormedArray:
            f.write(info+'\n')
        f.write('---------------------------------\n')
