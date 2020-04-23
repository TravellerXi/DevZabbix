#!/usr/bin/python3

# coding:utf-8
'''
RemoteUrl
RemoteServer

'''

from flask import Flask,request,session,redirect,Response,make_response
import requests
from contextlib import closing
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
requests.packages.urllib3.disable_warnings()

app =Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'cfomp@2020'
RemoteUrl='https://zabbix.mytlu.cn'
#RemoteServer=RemoteUrl[RemoteUrl.find('//')+2:]
RemoteServer='zabbix.mytlu.cn'

TeZhenMa='''<div class="signin-container">'''

htmlcode='''
<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="X-UA-Compatible" content="IE=Edge"/>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<meta name="Author" content="Zabbix SIA" />
		<title>Zabbix</title>
		<link rel="icon" href="favicon.ico">
		<link rel="apple-touch-icon-precomposed" sizes="76x76" href="assets/img/apple-touch-icon-76x76-precomposed.png">
		<link rel="apple-touch-icon-precomposed" sizes="120x120" href="assets/img/apple-touch-icon-120x120-precomposed.png">
		<link rel="apple-touch-icon-precomposed" sizes="152x152" href="assets/img/apple-touch-icon-152x152-precomposed.png">
		<link rel="apple-touch-icon-precomposed" sizes="180x180" href="assets/img/apple-touch-icon-180x180-precomposed.png">
		<link rel="icon" sizes="192x192" href="assets/img/touch-icon-192x192.png">
		<meta name="csrf-token" content=""/>
		<meta name="msapplication-TileImage" content="assets/img/ms-tile-144x144.png">
		<meta name="msapplication-TileColor" content="#d40000">
		<meta name="msapplication-config" content="none"/>
<link rel="stylesheet" type="text/css" href="assets/styles/blue-theme.css" />
<style type="text/css">.na-bg, .na-bg input[type="radio"]:checked + label, .na-bg:before, .flh-na-bg, .status-na-bg { background-color: #97AAB3 }
.info-bg, .info-bg input[type="radio"]:checked + label, .info-bg:before, .flh-info-bg, .status-info-bg { background-color: #7499FF }
.warning-bg, .warning-bg input[type="radio"]:checked + label, .warning-bg:before, .flh-warning-bg, .status-warning-bg { background-color: #FFC859 }
.average-bg, .average-bg input[type="radio"]:checked + label, .average-bg:before, .flh-average-bg, .status-average-bg { background-color: #FFA059 }
.high-bg, .high-bg input[type="radio"]:checked + label, .high-bg:before, .flh-high-bg, .status-high-bg { background-color: #E97659 }
.disaster-bg, .disaster-bg input[type="radio"]:checked + label, .disaster-bg:before, .flh-disaster-bg, .status-disaster-bg { background-color: #E45959 }

</style><script>var PHP_TZ_OFFSET = 28800,PHP_ZBX_FULL_DATE_TIME = "Y-m-d H:i:s";</script><script src="js/browsers.js"></script>
</head>
<body lang="en">
<output class="msg-global-footer msg-warning" id="msg-global-footer"></output>
<main><div class="signin-container"><div class="signin-logo"></div><form method="post" action="index.php" accept-charset="utf-8" aria-label="Sign in"><ul><li><label for="name">Username</label><input type="text" id="name" name="name" value="" maxlength="255" autofocus="autofocus"></li><li><label for="password">Password</label><input type="password" id="password" name="password" value="" maxlength="255"></li>
<li><label for="captcha">验证码(不区分大小写)</label><input type="text" id="captcha" name="captcha" value="" maxlength="255"><br/><img src="/imgcode" id="captcha_img" onclick="this.src='/imgcode'" width="auto" height="auto">
<a href="javascript:void(0)" onclick="document.getElementById('captcha_img').src='/imgcode?r='+Math.random()">换一个?</a><br/></li><li><input type="checkbox" id="autologin" name="autologin" value="1" class="checkbox-radio" checked="checked"><label for="autologin"><span></span>Remember me for 30 days</label></li><li><button type="submit" id="enter" name="enter" value="Sign in">Sign in</button></li></ul></form></div><div class="signin-links"><a target="_blank" class="grey link-alt" href="https://www.zabbix.com/documentation/4.0/">Help</a>&nbsp;&nbsp;•&nbsp;&nbsp;<a target="_blank" class="grey link-alt" href="https://www.zabbix.com/support">Support</a></div></main><footer role="contentinfo">&copy; 2001&ndash;2020, <a class="grey link-alt" target="_blank" href="https://www.zabbix.com/">Zabbix SIA</a></footer></body>

'''

def validate_picture():
    total = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
    # 图片大小130 x 50
    width = 130
    heighth = 50
    # 先生成一个新图片对象
    im = Image.new('RGB',(width, heighth), 'white')
    # 设置字体
    font = ImageFont.truetype('times.ttf', 40)  # ###Windows 'times.ttf', Linux 'wqy-microhei.ttc'
    # 创建draw对象
    draw = ImageDraw.Draw(im)
    str = ''
    # 输出每一个文字
    for item in range(5):
        text = random.choice(total)
        str += text
        draw.text((5+random.randint(4,7)+20*item,5+random.randint(3,7)), text=text, fill='black',font=font )

    # 划几根干扰线
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1),(x2,y2)), fill='black', width=1)

    # 模糊下,加个帅帅的滤镜～
    im = im.filter(ImageFilter.FIND_EDGES)
    return (im, str)


@app.before_request
def before_request():
    if ((request.full_path.find('/?')>-1 or request.full_path=='/index.php' or request.full_path=='/index.php?' )) and request.cookies.get('zbx_sessionid') is None :
        if  request.method=='GET':
            return htmlcode
        elif request.method=='POST':
            if request.form['captcha'].lower()==session['captcha'].lower():
                if (request.form['name']=='') or (request.form['password']==''):
                    return ('未输入用户名或密码，请重新输入<br><a href="/index.php?reconnect=1">返回登录</a>')
                else:
                    mycookies = request.cookies
                    url = RemoteUrl + request.full_path
                    method = request.method
                    data = request.data or request.form or None
                    headers = dict()
                    for name, value in request.headers:
                        if name == 'Host':
                            headers[name] = RemoteServer
                            continue
                        if name == 'Referer':
                            headers[name] = RemoteUrl
                            continue
                        if not value or name == 'Cache-Control':
                            continue
                        headers[name] = value
                        

                    headers['Host'] = RemoteServer
                    with closing(
                            requests.request(method, url, headers=headers, data=data, stream=True, cookies=mycookies,verify=False)
                    ) as r:
                        resp_headers = []
                        for name, value in r.headers.items():
                            if name.lower() in ('content-length', 'connection',
                                                'content-encoding'):
                                continue
                            resp_headers.append((name, value))
                        print(len(r.text))
                        if str(r.text).find(TeZhenMa)>-1:
                            return ('用户名或者密码错误，请重新登陆<br>'+htmlcode)
                        else:
                            print(Response(r.content, status=r.status_code, headers=resp_headers))
                            return Response(r, status=r.status_code, headers=resp_headers,mimetype='text/html')
            else:
                return ('验证码错误，请重新输入（不区分大小写）<br>'+htmlcode)
        else:
            return('非法操作')
    elif request.full_path.find('/imgcode?')>-1:
        if request.method == 'GET':
            image, Code = validate_picture()
            session['captcha'] = Code
            buf = BytesIO()
            image.save(buf, 'jpeg')
            buf_str = buf.getvalue()
            response = make_response(buf_str)
            response.headers['Content-Type'] = 'image/gif'
            return response
        else:
            return('非法操作')

    elif request.full_path == '/index.php?reconnect=1':
        response = redirect('/index.php')
        response.delete_cookie('zbx_sessionid')
        response.delete_cookie('session')
        response.delete_cookie('PHPSESSID')
        return response
    else:
        mycookies = request.cookies
        url = RemoteUrl + request.full_path
        method = request.method
        data = request.data or request.form or None
        headers = dict()
        for name, value in request.headers:
            if name == 'Host':
                headers[name] = RemoteServer
                continue
            if name == 'Referer':
                headers[name] = RemoteUrl
                continue
            if not value or name == 'Cache-Control':
                continue

            headers[name] = value
        headers['Host'] = RemoteServer
        with closing(
                requests.request(method, url, headers=headers, data=data, stream=True, cookies=mycookies,verify=False)
        ) as r:
            resp_headers = []
            for name, value in r.headers.items():
                if name.lower() in ('content-length', 'connection',
                                    'content-encoding'):
                    continue
                resp_headers.append((name, value))
            return Response(r, status=r.status_code, headers=resp_headers)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True,threaded=True)
