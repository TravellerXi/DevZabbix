#!/usr/bin/env python3
# coding:utf-8
import requests
from python2.CorpInfo import *

def TransferIDToName(Userid):
    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret).json()
    if not (GetResponse['errcode'] == 0):
        print('接收微信access_token失败')
        return 0
    access_token = (GetResponse['access_token'])

    get_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=' + access_token+'&userid='+Userid
    try:
        GetContent = requests.get(get_url)
        GetContent_ErrorCode = GetContent.json()['errcode']
        if not (GetContent_ErrorCode == 0):
            return('微信系统返回错误')
        else:
            print(GetContent.json()['name'])
            return (GetContent.json()['name'])
    except:
        print('get发送失败')
        return -1
