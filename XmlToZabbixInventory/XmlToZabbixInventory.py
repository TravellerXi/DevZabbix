#!/usr/bin/env python3
# coding:utf-8

'''
for coverting xml to Zabbix host inventory
'''

import xml.dom.minidom
from pyzabbix import ZabbixAPI, ZabbixAPIException
import warnings

def CheckIfhostExist(hostname):
    if (zapi.host.get(output=['host'], filter={'host': hostname}))==[]:
        return 0
    else:
        return 1


def ReturnRawDataFromXml(FileDir):
    '''
    :param FileDir: XML file dir
    :return: xml.dom的RAW data
    '''
    XmlFile = xml.dom.minidom.parse(FileDir)
    RawData = XmlFile.documentElement
    return RawData

def ReturnFormatedDataFromXml(FileDir):
    '''
    :param FileDir: XML file dir
    :return: list type
    '''
    ItBianma = []
    ShenchanRiqi = []
    DeviceMode = []
    DeviceSN = []
    CunfangJigui = []
    CunfangUwei = []
    IP1=[]
    IP2=[]
    ComputerName=[]
    ZichanBianma=[]
    iteminfo = ['IT编码', '生产日期', '设备型号', '设备SN', '存放机柜', '存放U位','IP1','IP2','计算机名','资产编码']
    for SpecificItem in iteminfo:
        Results = ReturnRawDataFromXml(FileDir).getElementsByTagName(SpecificItem)
        for Result in Results:
            if SpecificItem == 'IT编码':
                if Result.childNodes == []:
                    ItBianma.append('')
                else:
                    ItBianma.append(Result.childNodes[0].data)
            if SpecificItem == '生产日期':
                if Result.childNodes == []:
                    ShenchanRiqi.append('')
                else:
                    ShenchanRiqi.append(Result.childNodes[0].data)
            if SpecificItem == '设备型号':
                if Result.childNodes == []:
                    DeviceMode.append('')
                else:
                    DeviceMode.append(Result.childNodes[0].data)
            if SpecificItem == '设备SN':
                if Result.childNodes == []:
                    DeviceSN.append('')
                else:
                    DeviceSN.append(Result.childNodes[0].data)
            if SpecificItem == '存放机柜':
                if Result.childNodes == []:
                    CunfangJigui.append('')
                else:
                    CunfangJigui.append(Result.childNodes[0].data)
            if SpecificItem == '存放U位':
                if Result.childNodes == []:
                    CunfangUwei.append('')
                else:
                    CunfangUwei.append(Result.childNodes[0].data)
            if SpecificItem == 'IP1':
                if Result.childNodes == []:
                    IP1.append('')
                else:
                    IP1.append(Result.childNodes[0].data)

            if SpecificItem == 'IP2':
                if Result.childNodes == []:
                    IP2.append('')
                else:
                    IP2.append(Result.childNodes[0].data)
            if SpecificItem == '计算机名':
                if Result.childNodes == []:
                    ComputerName.append('')
                else:
                    ComputerName.append(Result.childNodes[0].data)
            if SpecificItem == '资产编码':
                if Result.childNodes == []:
                    ZichanBianma.append('')
                else:
                    ZichanBianma.append(Result.childNodes[0].data)

    TotalData = []
    i = 0
    while i < len(ItBianma):
        eachData = {'ItBianma': ItBianma[i], 'ShenchanRiqi': ShenchanRiqi[i], 'DeviceMode': DeviceMode[i],
                    'DeviceSN': DeviceSN[i], 'CunfangJigui': CunfangJigui[i], 'CunfangUwei': CunfangUwei[i],'IP1':IP1[i],'IP2':IP2[i],'ComputerName':ComputerName[i],'ZichanBianma':ZichanBianma}
        TotalData.append(eachData)
        i = i + 1
    return TotalData

def getInventorydata(hostname,item):
    '''
    :param hostname: Hostname,string
    :param item: string, Host Inventory item. check correct Host inventory item value from https://www.zabbix.com/documentation/4.0/zh/manual/api/reference/host/object
    :return: return value for specific item.
    need to login zabbix api before use this function.
    '''

    try:
        for h in zapi.host.get(output=['host'], filter={'host': hostname},
                               selectInventory=[item]):
            return h['inventory'][item]
    except:
        return 0


def ReturnHostidFromHostname(hostname):
    '''
    for get hostid
    :param hostname: hostname, string
    :return: hostid, string.
    '''
    for h in zapi.item.get(output=[ "hostid"], host=hostname):
        return h['hostid']



def WriteInventoryToZabbix(InventoryItem,host,hostname):
    '''
    WriteInventoryToZabbix By API
    :param InventoryItem: list, like ['tag','date_hw_purchase','asset_tag','site_rack','model']
    :param host: list
    :param hostname: string
    :return: 1
    '''
    for Item in InventoryItem:
        if Item == 'tag':
            inventoryvalue = 'IT编码: ' + str(host['ItBianma'])
            if getInventorydata(hostname, Item) == '':
                zapi.host.update(hostid=ReturnHostidFromHostname(hostname), inventory={Item: inventoryvalue})
            else:
                print(hostname + ' ' + Item + '已经有值，跳过写入...')
        if Item == 'date_hw_purchase':
            inventoryvalue = '生产日期:' + str(host['ShenchanRiqi'])
            if getInventorydata(hostname, Item) == '':
                zapi.host.update(hostid=ReturnHostidFromHostname(hostname), inventory={Item: inventoryvalue})
                print(hostname+' '+Item+'写入成功')
            else:
                print(hostname + ' ' + Item + '已经有值，跳过写入...')
        if Item == 'asset_tag':
            inventoryvalue = '资产编码:' + str(host['ZichanBianma'][0]) + ',' + '设备SN:' + str(host['DeviceSN'])
            if getInventorydata(hostname, Item) == '':
                zapi.host.update(hostid=ReturnHostidFromHostname(hostname), inventory={Item: inventoryvalue})
                print(hostname + ' ' + Item + '写入成功')
            else:
                print(hostname + ' ' + Item + '已经有值，跳过写入...')
        if Item == 'site_rack':
            inventoryvalue = '存放机柜:' + str(host['CunfangJigui'] )+ ',' + '存放U位:' + str(host['CunfangUwei'])
            if getInventorydata(hostname, Item) == '':
                zapi.host.update(hostid=ReturnHostidFromHostname(hostname), inventory={Item: inventoryvalue})
                print(hostname + ' ' + Item + '写入成功')
            else:
                print(hostname+ ' ' + Item + '已经有值，跳过写入...')
        if Item == 'model':
            inventoryvalue =str(host['DeviceMode'])
            if getInventorydata(hostname, Item) == '':
                zapi.host.update(hostid=ReturnHostidFromHostname(hostname), inventory={Item: inventoryvalue})
                print(hostname + ' ' + Item + '写入成功')
            else:
                print(hostname + ' ' + Item + '已经有值，跳过写入...')
    return 1

def Execute(XmlDir):
    '''
    Read XML file, process data and update it to Zabbix Host Inventory if target is blank.
    :param XmlDir: string type.
    :return: 1
    '''
    InventoryItem = ['tag', 'date_hw_purchase', 'asset_tag', 'site_rack', 'model']
    Hosts = ReturnFormatedDataFromXml(XmlDir)
    for host in Hosts:
        if CheckIfhostExist(str(host['IP1']))>0:
            print('try ' + str(host['IP1']))
            hostname = str(host['IP1'])
            WriteInventoryToZabbix(InventoryItem, host, hostname)

        elif CheckIfhostExist(str(host['IP2']))>0:
            print(' try '+str(host['IP2']))
            hostname = str(host['IP2'])
            WriteInventoryToZabbix(InventoryItem, host, hostname)
        elif CheckIfhostExist(str(host['ComputerName']))>0:
            print( 'try ' + str(host['ComputerName']))
            hostname = str(host['ComputerName'])
            WriteInventoryToZabbix(InventoryItem, host, hostname)
        else:
            print('cannot find any ip: '+str(host['IP1'])+'、 '+str(host['IP2'])+' or hostname '+str(host['ComputerName'])+' '+' on Zabbix.')
    print('写入完毕')
    return 1

if __name__ =="__main__":
    warnings.filterwarnings('ignore')
    ZABBIX_SERVER = 'https://domain.com/'
    zapi = ZabbixAPI(ZABBIX_SERVER)
    # Disable SSL certificate verification
    zapi.session.verify = False
    zapi.login("username", "passwd")
    XmlDir='C:\\Users\\Quantdo\\OneDrive\\工作\\配置基线-Zabbix开发\\updata-inventory\\test.xml'
    Execute(XmlDir)

