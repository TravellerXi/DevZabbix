#!/usr/bin/env python3
# coding:utf-8
from pyzabbix import ZabbixAPI
import warnings
from python2.CorpInfo import *
from TransferWechatworkIDToUserName import *

def HandleUserSendTxt(text:str,UserID):
    HelpContent='以下为帮助信息：\n发送“ack+空格+故障ID+空格+回复内容”可确认问题，并发送消息给所有跟故障有关的人员\n例: ack 3773316 请XXX立即处理该问题\n'+\
        '发送“info+空格+主机名”可获取主机的硬件信息(主机名可在Zabbix中查询)\n例： info 网站中间件\n发送“帮助”或“help”获取帮助信息'
    if text.find('ack')>-1:
        text=text[4:]
        ReplyContent = ''
        EventID=''
        if text.find(' ')==-1:
            EventID=text
            ReplyContent=''
        else:
            EventID = text[:text.find(' ')]
            ReplyContent = text[text.find(' ') + 1:]
        username = TransferIDToName(UserID)
        ReplyToAllInvolved(ReplyContent, EventID, username)
        return 1
    elif text.find('info')>-1:
        text=text[5:]
        HostName=text
        RawData='以下是主机的硬件信息：\n'
        RawData=RawData+GetHostInventoryFromHostName(HostName)
        return (RawData)
    elif  text.find('帮助') >-1 or text.find('HELP')>-1 or text.find('Help')>-1 or text.find('help')>-1:
        return(HelpContent)
    else:
        return ('指令不正确\n'+HelpContent)



def GetHostInventoryFromHostName(HostName):
    InventoryNameList={
        'type':'Type',
        'name':'Name',
        'alias':'Alias',
        'os':'OS',
        'os_full':'OS(Fulldetails)',
        'os_short':'OS(Short)',
        'serialno_a':'Serial number A',
        'serialno_b':'Serialnumber B',
        'software':'Software',
        'location':'Location',
        'location_lat':'Location latitude',
        'location_lon':'Location longitude',
        'model':'Model',
        'hw_arch':'HW architecture',
        'vendor':'Vendor',
        'date_hw_purchase':'Date HW purchased',
        'site_address_a':'Siteaddress A',
        'site_address_b':'Siteaddress B',
        'site_address_c':'Siteaddress C',
        'site_state':'Site state / province',
        'site_country':'Site country',
        'site_zip':'Site ZIP / postal',
        'site_rack':'Site rack location',
        'site_notes':'Site notes',
        'poc_2_name':'Secondary POC name',
        'poc_2_email':'Secondary POC email',
        'poc_2_phone_a':'Secondary POC phone A',
        'poc_2_phone_b':'Secondary POC phone B',
        'poc_2_cell':'Secondary POC cell',
        'poc_2_screen':'Secondary POC screen name',
        'poc_2_notes':'Secondary POC notes'
    }
    Inventorys=[]
    for i in InventoryNameList:
        Inventorys.append(i)
    url = URL  # 这里的URL在python2.CorpInfo 定义
    zapi = ZabbixAPI(server=url)
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)
    InventoryCotent = zapi.host.get(search={'host':[HostName]}, withInventory=1,
                      selectInventory=Inventorys)
    RawContent = ''
    if InventoryCotent==[]:
        RawContent='未匹配到该主机的信息，可能是主机名填写错误，请检查主机名是否存在于Zabbix系统'
    else:
        InventoryCotent=InventoryCotent[0]['inventory']
    for content in InventoryCotent:
        RawContent=RawContent+InventoryNameList[content]+': '
        RawContent=RawContent+InventoryCotent[content]+'\n'
    return (RawContent)

def ReplyToAllInvolved(ReplyContent,EventID,username):
    url = URL  # 这里的URL在python2.CorpInfo 定义
    zapi = ZabbixAPI(server=url)
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)
    ReplyContent=username+'评论道: '+ReplyContent
    zapi.event.acknowledge(eventids=str(EventID), action='6', message=ReplyContent)
    return 1
