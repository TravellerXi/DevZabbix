#!/usr/bin/env python3
# coding:utf-8
from pyzabbix import ZabbixAPI
import warnings


if __name__ == '__main__':
    ZABBIX_SERVER = 'https://serveraddress.com'
    zapi = ZabbixAPI(ZABBIX_SERVER)
    warnings.filterwarnings('ignore')
    # Disable SSL certificate verification
    zapi.session.verify = False
    zapi.login("username", "password")
    SnmpUnreachable=zapi.host.get()
    hostnames = []
    for host in SnmpUnreachable:
        if host['snmp_available']=='2':
            hostnames.append(host['host'])
    with open ('Snmp不可达主机列表.txt','w') as f:
        for hostname in hostnames:
            f.write(hostname+'\n')
    print('任务完毕')
