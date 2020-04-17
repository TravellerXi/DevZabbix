#!/usr/bin/env python3
# coding:utf-8

"""
this script is running based on Windows zabbix agent.

"""


from pyzabbix import ZabbixAPI
import warnings
import csv
import os

def ReturnSingleFormedDataFromZabbixInventory(data):
    '''
    Return Formed data from zabbix inventory, specific host inventory content like: 资产编码:test,设备SN:06EPGCE
    该函数专门处理Host inventory里存在多个数据的。
    :param data: string type，zabbix api拿到的数据。
    :return:形如: [{'存放机柜': 'A07'}, {'存放U位': '26'}]
    '''
    FormedData=[]
    try:
        for eachdata in data.split(','):
            FormedData.append({eachdata.split(':')[0]: eachdata.split(':')[1]})
        return FormedData
    except:
        return []


def ReturnAllFormedDataForZabbixInventory(host):
    '''
    ReturnSingleFormedDataFromZabbixInventory的变体，可以返回下面定义InventoryItem里的所有值，并组合成一个
    :param host: string type.
    :return: 返回值形如:[{'IT编码': ' BA000465'}, {'生产日期': '2015/2/12'}, {'资产编码': 'test'}, {'设备SN': '06EPGCE'}, {'存放机柜': 'A07'}, {'存放U位': '26'}]
    '''
    AllRawData = []
    InventoryItem = ['tag', 'date_hw_purchase', 'asset_tag', 'site_rack']
    for Item in InventoryItem:
        for EachItem in (ReturnSingleFormedDataFromZabbixInventory(getInventorydataFromHostName(host, Item))):
            AllRawData.append(EachItem)
    return(AllRawData)

def CheckIfWindowsorLinux(host):
    '''
    :param host: hostname,string
    :return: 1: windows, 0: Linux 或者不是期望的Windows主机
    '''
    systeminfo = getValueFromHost(host, 'OS windows directory')
    if systeminfo is not None and (systeminfo > '' or systeminfo < ''):
        return 1
    else:
        return 0

def ReturnCipanSize(host):
    '''
    Windows Zabbix Agent use only. Linux agent获取数据会出问题。
    :param host: hostname, string type
    :return: return 2 list, cipan and size
    '''
    disk = []
    for h in zapi.item.get(output=["itemid", "name", "hostid", "value_type", "lastvalue", 'key_'], host=host,
                           search={"name": '*' + 'Total disk space on' + '*'}, searchWildcardsEnabled='1'):
        disk = disk + [{'CiPan': h['key_'][12:13], 'size': h['lastvalue']}]

    cipan = []
    size = []
    for eachdisk in disk:
        cipan.append(eachdisk['CiPan']+'盘容量')
        size.append(str(int(eachdisk['size'])/1024/1024/1024)+' G')
    return (cipan,size)

def WriteinfoToCsv(filename,itemname,iteminfo,dir):
    '''
    :param filename:String类型
    :param itemname:list类型
    :param iteminfo:list类型
    :param dir: string type,filedir,哪里放置CSV文件
    :return: 1
    '''
    with open(dir+filename, 'w',newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(itemname)
        writer.writerow(iteminfo)
    return 1



def getValueFromHost(host,itemName):
    '''
    :param host: host name,usually ip,like '10.189.66.131',but need to be string type.
    :param itemName: like "*cpu_model*", need to be string type.
    :return: The last value of itemName for specific 'host'. String type.
    '''
    for h in zapi.item.get(output=["itemid", "name", "hostid", "value_type", "lastvalue"], host=host,
                           search={"name": '*'+itemName+'*'}, searchWildcardsEnabled='1'):
        return (h['lastvalue'])

def getValueFromItem(host,item):
    '''
    :param host: string
    :param item: item: list
    :return:  return list
    '''
    data=[]
    for eachItem in item:
        if eachItem=='Total memory':
            if getValueFromHost(host, eachItem) is None:
                data.append('')
            else:
                data.append(str(int(getValueFromHost(host, eachItem))/1024/1024/1024)+' G')
        elif eachItem=='Diskdrive size':
            if getValueFromHost(host, eachItem) is None:
                data.append('')
            else:
                data.append(str(int(getValueFromHost(host, eachItem)) / 1024 / 1024 / 1024) + ' G')
        else:
            data.append(getValueFromHost(host,eachItem))
    return data

def getInventorydataFromHostName(hostname,item):
    '''
    :param hostname: Hostname,string
    :param item: string, itemname.
    :return: return value for specific item.
    need to login zabbix api before use this function.
    '''

    for h in zapi.host.get(output=['host'], filter={'host': hostname},
                           selectInventory=[item]):
        return h['inventory'][item]

def WriteServerAllInfotoCsv(host,Dir):
    '''
    :param host: hostname, string type
    :param Dir: where we put the file
    :return: 1
    '''

    HostDir=Dir+'\\'+host+'\\'
    try:
        os.mkdir(HostDir)
        os.mkdir(HostDir+'服务器')
        os.mkdir(HostDir + '配置文件')
        os.mkdir(HostDir + '应用服务')
    except:
        print('folder ' +HostDir+' already exist,skip make dir for '+host+'...')
    HostDir = Dir + '\\' + host + '\\服务器'+'\\' ######写入此目录下

    ####    here is cpu list:
    itemBeforeZhupin = ['Cpu model', 'Cpu number of logical processors']
    itemAfterZhupin=['Cpu number of cores']
    ZhuPin=(getValueFromItem(host,['Cpu model'])[0][(getValueFromItem(host,['Cpu model'])[0].find('@'))+1:])
    ItemValue=getValueFromItem(host,itemBeforeZhupin)
    ItemValue.append(ZhuPin)
    for item in getValueFromItem(host,itemAfterZhupin):
        ItemValue.append(item)
    itemChinese = ['品牌型号', '逻辑个数', '主频', '核数', '备注']
    WriteinfoToCsv('cpu.csv', itemChinese, ItemValue,HostDir)

##### 端口列表
    itemChinese=['业务端口']
    with open(HostDir + '端口列表.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(itemChinese)

    ###   here is 内存 list:
    item = ['Total memory', 'Mem model']
    itemChinese = ['容量', '型号', '备注']
    WriteinfoToCsv('内存.csv', itemChinese, getValueFromItem(host, item),HostDir)

    # here is 硬盘 list:
    Diskinfo=ReturnCipanSize(host)
    itemWithoutDisk = ['Diskdrive interface type', 'Diskdrive size', 'Diskdrive model']
    itemChinese = ['驱动器类型', '总容量', '型号']
    for cipan in Diskinfo[0]:
        itemChinese.append(cipan)
    itemChinese.append('备注')
    itemValue=getValueFromItem(host, itemWithoutDisk)
    for size in Diskinfo[1]:
        itemValue.append(size)
    WriteinfoToCsv('硬盘.csv', itemChinese, itemValue,HostDir)

    ####  here is 操作系统 list:
    item = ['OS Caption', 'OS CodeSet', 'OS CSDVersion', 'OS InstallDate', 'OS OSArchitecture', 'OS OSLanguage',
            'OS OSType', 'OS SerialNumber', 'OS version', 'OS windows directory', 'Server host name',
            'Manufacturer', 'Product Name', 'Server serial number']
    itemChinese = ['系统名称', '系统字符集', 'Service Pack', '安装日期', '32位/64位',
                   '系统语言版本', '系统类型', '系统产品序列号', '补丁版本号',
                   '系统目录', '主机名', '服务器制造商', '服务器型号', '服务器序列号', '说明']
    WriteinfoToCsv('操作系统.csv', itemChinese, getValueFromItem(host, item),HostDir)

    #### IP列表
    item = ['Network adapter type', 'Network maxspeed', 'Network product name',
            'Network mac address','Network networkaddresses']
    itemChinese = ['网卡类型', '网卡最大速度',  '网卡产品名称', '网卡MAC地址','网卡IP地址','掩码','网关','说明']
    WriteinfoToCsv('ip列表.csv', itemChinese, getValueFromItem(host, item),HostDir)

    ### 计算机名称
    item = ['Server host name']
    itemChinese = ['计算机名称', '计算节点名称','虚拟机操作系统名称']
    WriteinfoToCsv('计算机名称.csv', itemChinese, getValueFromItem(host, item),HostDir)

    ### 基本信息
    itemChinese=['计算机类型','虚拟机类型','状态','应用名称','资产标签','SN序列号','OA流程编号','IT验收编码','资产编码']
    itemValue=['','','','','',ReturnAllFormedDataForZabbixInventory(host)[3]['设备SN'],'',ReturnAllFormedDataForZabbixInventory(host)[0]['IT编码'],ReturnAllFormedDataForZabbixInventory(host)[2]['资产编码']]
    #itemValue.append(getInventorydataFromHostName(host, 'serialno_a'))
    WriteinfoToCsv('基本信息.csv', itemChinese, itemValue,HostDir)

    #### 应用服务
    itemChinese=['编号','应用服务名称','安装路径','配置文件路径+名称','应用服务安装包名称','是否配置系统变量','是否需要安装','备注']
    with open(Dir + '\\' + host + '\\应用服务'+'\\' + '应用服务.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(itemChinese)

    ####  服务器型号
    item = ['Manufacturer', 'Product Name']
    itemChinese = ['服务器品牌', '设备型号']
    WriteinfoToCsv('服务器型号.csv', itemChinese, getValueFromItem(host, item),HostDir)

    ###   物理位置
    itemChinese=['服务器物理位置','所属机柜','机柜位置']
    LocationValue=[]
    try:
        LocationValue.append(str(getInventorydataFromHostName(host, 'location')))
    except:
        LocationValue.append('')
    try:
        LocationValue.append(ReturnAllFormedDataForZabbixInventory(host)[4]['存放机柜'])
    except:
        LocationValue.append('')
    try:
        LocationValue.append(ReturnAllFormedDataForZabbixInventory(host)[5]['存放U位'])
    except:
        LocationValue.append('')
    WriteinfoToCsv('物理位置.csv', itemChinese, LocationValue, HostDir)

    #### 系统环境变量
    #item = ['OS environment']
    itemChinese = ['系统环境', '备注']
    WriteinfoToCsv('系统环境变量.csv', itemChinese, '',HostDir)

    ####  安全配置
    item = ['Status of Windows Firewall', 'Symantec Endpoint Protection']
    itemChinese = ['本机防火墙', '防病毒软件', '安全基线完成情况']
    WriteinfoToCsv('安全配置.csv', itemChinese, getValueFromItem(host, item),HostDir)
    return 1

def ReturnHostFromGroupName(groupname):
    '''
    :param groupname:  name of group, string type
    :return: hostname, list type
    '''
    hostlist=[]
    for h in zapi.hostgroup.get(output='extend', filter={'name': groupname}):
        groupid = h['groupid']
    for h in zapi.host.get(groupids=groupid):
        hostlist.append(h['host'])
    return hostlist

if __name__ =="__main__":
    warnings.filterwarnings('ignore')
    Dir = 'E:\A02-股票期权\computer_info' ### CSV放置根目录
    ZABBIX_SERVER = 'https://domain.com/'
    zapi = ZabbixAPI(ZABBIX_SERVER)
    # Disable SSL certificate verification
    zapi.session.verify = False
    zapi.login("username", "passwd")
    for host in ReturnHostFromGroupName('Zabbix servers'): ###哪些群组需要使用脚本
        if CheckIfWindowsorLinux(host)>0:
            print(host +' is the specific Windows, work on writting info to CSV file...')
            WriteServerAllInfotoCsv(host,Dir)
        else:
            print(host+' is not the specific Windows or is Linux, ignore..')
    print('Done!')
