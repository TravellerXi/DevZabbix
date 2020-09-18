#!/usr/bin/env python3
# coding:utf-8
import requests
import json
from python2.CorpInfo import *


def SendMessageByApplication(UserList,Content):

    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])
    touser = ''
    for i in UserList:
        touser = touser + i
    rawdata = {
        'touser': touser,
        'msgtype': "text",
        'agentid': AgentID,
        'text': {
            'content': Content
        },
        'safe': 0,
        'enable_id_trans': 0,
        'enable_duplicate_check': 0
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    try:
        PostContent = requests.post(post_url, json.dumps(rawdata))
        PostContent_ErrorCode = PostContent.json()['errcode']
        if not (PostContent_ErrorCode == 0):
            print('微信系统返回错误')
            return 0
        else:
            return 1
    except:
        print('post发送失败')
        return 0


def SendCardMessageByTaskCardToApp(UserId,Subject,Message,task_id):

    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])
    FormedArray = Message.split('---')
    print(FormedArray)
    FormedArray[0] = "发生时间：" + FormedArray[0] + ' '
    FormedArray[1] = "on " + FormedArray[1] + '\n'
    FormedArray[2] = "故障名：" + FormedArray[2] + '\n'
    FormedArray[3] = "<div class=\"highlight\">主机名：" + FormedArray[3] + '</div>'
    FormedArray[4] = "<div class=\"highlight\>主机IP:" + FormedArray[4] + '</div>'
    FormedArray[5] = "<div class=\"highlight\>故障等级:" + FormedArray[5] + '</div>\n'
    FormedArray[6] = "<div class=\"gray\">Original problem ID：" + FormedArray[6] + '</div>'
    Content = ''
    for data in FormedArray:
        Content = Content + data
    print(Content)
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


def UpdateTaskCardToApp(UserId,TaskID,clicked_key):

    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])
    rawdata = {
    "userids" : [UserId],
    "agentid" : AgentID,
    "task_id": TaskID,
    "clicked_key": clicked_key
}

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/update_taskcard?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    print(PostContent.json())
    print(rawdata)
    return 1

def SendTextToApp(UserId,Content):

    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])
    rawdata = {
   "touser" : UserId,
   "msgtype" : "text",
   "agentid" : AgentID,
   "text" : {
       "content" : Content
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/update_taskcard?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    print(PostContent.json())
    print(rawdata)
    return 1