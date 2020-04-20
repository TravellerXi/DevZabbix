#!/usr/bin/env python3
# coding:utf-8

'''
为了解决需求：
编写程序，筛选zabbix host inventory中location== '科技网机房'的主机的主机群组

统计每个群组有这样的主机的数量，并写入CSV文件
'''
from pyzabbix import ZabbixAPI, ZabbixAPIException
import warnings
import csv




def getInventorydataFromHostName(hostname,item):
    '''
    :param hostname: Hostname,string
    :param item: string, itemname.
    :return: return value for specific item.
    need to login zabbix api before use this function.
    '''

    for h in zapi.host.get(output=['host'], filter={'host': hostname},
                           selectInventory=[item]):
        if h['inventory']==[]:
            return ('')
        else:
            return (str(h['inventory'][item]))

def WriteinfoToCsv(filename,itemone,itemtwo,dir):
    '''
    :param filename:String类型
    :param itemname:list类型
    :param iteminfo:list类型
    :param dir: string type,filedir,哪里放置CSV文件
    :return: 1
    '''
    with open(dir+filename, 'w',newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(itemone)
        writer.writerow(itemtwo)
    return 1

def CheckIfHostKejiwang(Filename):
    '''
    检查得出所有Host inventory location项目值为'科技网机房'的主机，并初步筛选出非自动发现创建的groups，主机写入CSV文件
    :param Filename:主机写入CSV文件名,string
    :param Dir:CSV存放地址，string
    :return:groups,HostInKejiwang。
    '''
    groups = []
    for h in zapi.hostgroup.get(output='extend'):
        #if h['flags'] > '4' or h['flags']<'4':###处理掉自动创建的hostgroup
        h.update(count=0)
        groups.append(h)
    HostInKejiwang = []
    for h in zapi.host.get(output=['host','hostid']):
        if getInventorydataFromHostName(h['host'], 'location') == '科技网机房':
            HostInKejiwang.append(h['hostid'])
    HostInKejiwangCount=0
    for host in HostInKejiwang:
        HostInKejiwangCount=HostInKejiwangCount+1
    ListHostInKejiwangCount=[]
    ListHostInKejiwangCount.append(HostInKejiwangCount)
   # WriteinfoToCsv(Filename,HostInKejiwang,ListHostInKejiwangCount,Dir)
    return (groups,HostInKejiwang)




def CompareHostWithHostgroup(groups,HostInKejiwang,Filename,Dir):
    '''对比筛选出来的host的hostgroupid与主机群组里的hostgroupid，如果一致，主机群组字典里count+1,count 初始为0，并写入Dir的Filename里。删掉主机群组里count为0的主机群组。
    :param groups:
    :param HostInKejiwang:
    :param Filename:
    :param Dir:
    :return:
    '''
    for hostid in HostInKejiwang:
        count=0
        groupid=zapi.hostgroup.get(output='extend', hostids=hostid)[0]['groupid']
        for group in groups:
            if groupid==group['groupid']:
                groups[count]['count']=groups[count]['count']+1
            count = count+1
    groupname = []
    groupcount = []
    for group in groups:
        if group['count'] > 0:
            groupname.append(group['name'])
            groupcount.append(group['count'])
    WriteinfoToCsv(Filename, groupname, groupcount, Dir)
    return 1



if __name__ =="__main__":
    warnings.filterwarnings('ignore')
    Dir = 'E:\\A02-股票期权\\computer_info\\' ### CSV放置根目录
    ZABBIX_SERVER = 'https://domain.com/'
    zapi = ZabbixAPI(ZABBIX_SERVER)
    # Disable SSL certificate verification
    zapi.session.verify = False
    zapi.login("username", "password")
    KejiwangHost=(CheckIfHostKejiwang('HostInKejiwang.csv'))

    groups=KejiwangHost[0]
    HostInKejiwang=KejiwangHost[1]
    CompareHostWithHostgroup(groups, HostInKejiwang, 'test2.csv', Dir)
    print('Done, 请检查'+Dir+'下CSV文件')



