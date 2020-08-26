#!/usr/bin/env python3
# coding:utf-8
from pyzabbix import ZabbixAPI
import warnings
import socket
'''
Purpose:
校验某个网段的SNMP IP 80或443端口是否开放，且是否在zabbix系统里录入，如录入，显示zabbix录入的业务IP
'''

def CheckHardIfHardwarePortIsOpen(ip:str):
    '''
    :param ip: 传入IP，检测IP的80和443端口是否开放
    :return: 开放返回1，不开放返回0
    '''
    socket.setdefaulttimeout(1)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((ip, 80))
        server.close()
        return 1

    except:
        try:
            server.connect((ip, 443))
            server.close()
            return 1
        except:
            return 0




def ReturnHostIpFromSnmpIp(snmpip):
    '''
    :param snmpip: string, snmpip
    :return: string, IP on Agent interfaces
    '''
    SnmpInterface=(zapi.hostinterface.get(output='extend',filter={'ip': snmpip,'type':'2'}))
    if SnmpInterface==[]:
        AgentInterface='Zabbix里无对应主机'
    else:
        AgentInterface=(zapi.hostinterface.get(output='extend',hostids=SnmpInterface[0]['hostid']))[0]['ip']
    return AgentInterface
if __name__ == '__main__':
    #ZABBIX_SERVER = 'http://10.188.66.180/zabbix'
    ZABBIX_SERVER = 'ZabbixUrlHere'
    zapi = ZabbixAPI(ZABBIX_SERVER)
    warnings.filterwarnings('ignore')
    # Disable SSL certificate verification
    zapi.session.verify = False
    # zapi.login("username", "passwd")
    zapi.login("username", "passwd")
    HardWareIpRange=[]
    Log = ''
    for j in range(1,255):
        i=str(j)
        HardWareIpRange.append('10.187.11.'+i)
        HardWareIpRange.append('10.187.12.'+i)
        HardWareIpRange.append('10.187.13.'+i)
        HardWareIpRange.append('10.187.21.'+i)
        HardWareIpRange.append('10.187.139.'+i)
        HardWareIpRange.append('10.187.140.'+i)
        HardWareIpRange.append('10.192.4.'+i)
        HardWareIpRange.append('10.187.200.'+i)
        HardWareIpRange.append('10.187.201.'+i)

    OpenPortHardwareIpRang=[]
    NotOpenPortHardwareIpRang=[]
    for i in HardWareIpRange:
        if CheckHardIfHardwarePortIsOpen(i)>0:
            OpenPortHardwareIpRang.append(i)
        else:
            NotOpenPortHardwareIpRang.append(i)

    Log=Log+'以下是经检测，端口80或者443开放的硬件管理口IP对应的Zabbix业务IP信息：\n'
    for i in OpenPortHardwareIpRang:
        try:
            print(i + '硬件主机IP对应的Zabbix 业务IP为： ' + ReturnHostIpFromSnmpIp(i))
            Log = Log + (i + '硬件主机IP对应的Zabbix 业务IP为： ' + ReturnHostIpFromSnmpIp(i) + '\n')
        except:
            print('在处理硬件主机IP' + i + '时，脚本发生了错误')
            Log = Log + '在处理硬件主机IP' + i + '时，脚本发生了错误\n'
    Log = Log + '以下是经检测，端口80或者443不开放的硬件管理口IP对应的Zabbix业务IP信息：\n'
    for i in NotOpenPortHardwareIpRang:
        try:
            print(i + '硬件主机IP对应的Zabbix 业务IP为： ' + ReturnHostIpFromSnmpIp(i))
            Log = Log + (i + '硬件主机IP对应的Zabbix 业务IP为： ' + ReturnHostIpFromSnmpIp(i) + '\n')
        except:
            print('在处理硬件主机IP' + i + '时，脚本发生了错误')
            Log = Log + '在处理硬件主机IP' + i + '时，脚本发生了错误\n'
    Log = Log + '写入端口80或者443开放的硬件管理口IP：\n'
    for i in OpenPortHardwareIpRang:
        Log=Log+i+'\n'
    Log = Log + '写入端口80或者443不开放的硬件管理口IP：\n'
    for i in NotOpenPortHardwareIpRang:
        Log=Log+i+'\n'
    with open('扫描IP段.log', 'a') as f:
        f.write(Log)

    print('扫描IP段完毕')


