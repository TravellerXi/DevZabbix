#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request,abort
from SendMsg import *
import os
from TransferWechatworkIDToUserName import *
from EventUpdate import *
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)


@app.route('/', methods=['GET'])
def basic_get():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        command = '/bin/python /api/python2/callback.py ' + msg_signature + ' ' + timestamp + ' ' + nonce + ' "' + echostr + '"'
        callback = os.popen(command).read()

        return (callback[:-1])
    except:
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
        ToUserName = ReceiveMsg[:-1].split(',')[3]

        ##我们从上面就获取了FromUserName和Content。下面我们要回复消息给微信
        if MsgType == 'text':
            # 处理纯文本事件
            UserList = [FromUserName]
            ReplyContent = '这是对你发送的的"' + Content + '"的回复'
            try:
                if not (SendMessageByApplication(UserList, ReplyContent)):
                    print('回复消息失败')
            except:
                print('回复消息失败')
            return ('')
        if MsgType == 'event':
            # 处理event里面的click事件
            EventID = ToUserName[:(ToUserName.find('@'))]
            ReplyContent = HandleZabbixEventUpdateRequest(EventID, Content, Username)
            if ReplyContent != '1':
                SendTextToApp(FromUserName, ReplyContent)

            try:
                if not (UpdateTaskCardToApp(FromUserName, ToUserName, SendCardMessageByTaskCardToApp)):
                    print('回复消息失败')
            except:
                print('回复消息失败')

        return ('')
    except:
        abort(404)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=824, debug=False,threaded=True)
