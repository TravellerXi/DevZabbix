#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request, abort
import os
# 以下导入各个文件里的函数
from SendMsg import *
from TransferWechatworkIDToUserName import *
from EventUpdate import *
from HandleUserSendTxt import *
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)


@app.route('/', methods=['GET'])
def basic_get():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        # 上述几个变量的详细介绍在https://work.weixin.qq.com/api/doc/90000/90135/90930
        # 下面，直接调用os来执行python2的代码，读取执行结果，返回回调信息。
        command = '/bin/python /api/python2/callback.py ' + msg_signature + ' ' + timestamp + ' ' + nonce + ' "' + echostr + '"'
        callback = os.popen(command).read()
        return (callback[:-1])
    except:
        # 当异常访问（非微信调用），会直接返回404（降低攻击）
        abort(404)

@app.route('/', methods=['POST'])
def basic_post():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        ReqData = request.get_data().decode()
        command = '/bin/python /api/python2/ReceiveMsg.py ' + msg_signature + ' ' + timestamp + ' ' + nonce + ' "' + ReqData + '"'
        ReceiveMsg = os.popen(command).read()
        # 在不同条件下，Content有时是消息内容有时是消息触发的动作，具体见python2/ReceiveMsg.py
        Content = ReceiveMsg[:-1].split(',')[0]
        FromUserName = ReceiveMsg[:-1].split(',')[1]
        Username = TransferIDToName(FromUserName)
        if Username == 0:
            print('该企业微信用户ID未找到用户名，ID为:' + FromUserName)
            return ('')
        elif Username == -1:
            print('转换企业微信ID失败')
            return ('')

        MsgType = ReceiveMsg[:-1].split(',')[2]
        # 在不同条件下，ToUserName有时可能是TaskId，具体见python2/ReceiveMsg.py
        ToUserName = ReceiveMsg[:-1].split(',')[3]
        # 我们从上面就获取了FromUserName和Content。下面我们要回复消息给微信
            # 此处处理用户发送的消息
        if MsgType == 'text':
            # 处理纯文本事件
            # ReplyContent = '这是对你发送的的"' + Content + '"的回复'
            # 调用 HandleUserSendTxt
            ReplyContent = HandleUserSendTxt(Content, FromUserName)
            # 如果发送的是含ack的信息
            if ReplyContent == 1:
                return ('')
            else:
                try:
                    if not (SendTextToApp(FromUserName, ReplyContent)):
                        print('回复消息失败')
                except:
                    print('回复消息失败')
                return ('')
        # 处理event里面的click事件,就是用户点击微信里的确认开始处理/关闭问题
        if MsgType == 'event' and ToUserName != 'myproblem':
            EventID = ToUserName[:(ToUserName.find('@'))]
            ReplyContent = HandleZabbixEventUpdateRequest(EventID, Content, Username)
            if ReplyContent != '1':
                SendTextToApp(FromUserName, ReplyContent)

            if not (UpdateTaskCardToApp(FromUserName, ToUserName, Content)):
                print('回复消息失败')
        #TODO :获取微信当前用户在zabbix里的所有问题
        #见GetUserProblem.py，待开发
        if MsgType == 'event' and ToUserName == 'myproblem':
            print('这是myproblem')
        return ('')
    except:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=824, debug=False,threaded=True)
