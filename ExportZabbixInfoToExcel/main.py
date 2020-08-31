#/usr/bin/env python3
#coding:utf-8
from pyzabbix import ZabbixAPI
import warnings
import argparse
import  pandas  as pd
from styleframe import StyleFrame
##增加styleframe以自适应Excel的列宽度



def WriteRawdataToExcel(ExcelContent:dict,Filename:str):
    '''
    :param ExcelContent: 生成的未处理的原始数据
    :param Filename: 生成的Excel文件名
    :return: 1
    '''
    #writer = pd.ExcelWriter(Filename)
    exwriter = StyleFrame.ExcelWriter(Filename)
    for GroupRealted in ExcelContent:
        GroupName=GroupRealted['groupname']
        Zhujiming=[]
        ZhujiIP=[]
        GuanliIP=[]
        Changshang=[]
        Xuliehao=[]
        Jifang=[]
        for HostRelated in GroupRealted['content']:
            hostname=HostRelated['hostname']
            Zhujiming.append(hostname)
            vendor=''
            serialno_a=''
            location=''

            try:
                vendor=HostRelated['inventory']['vendor']
            except:
                vendor = ''
            Changshang.append(vendor)
            try:
                serialno_b=HostRelated['inventory']['serialno_b']
            except:
                serialno_b=''
            Xuliehao.append(serialno_b)
            try:
                location=HostRelated['inventory']['location']
            except:
                location=''
            Jifang.append(location)

            for InterfaceRelated in HostRelated['interfaces']:
                try:
                    AgentInterface=InterfaceRelated['1']
                except:
                    AgentInterface=''
                ZhujiIP.append(AgentInterface)
                try:
                    SnmpInterface=InterfaceRelated['2']
                except:
                    SnmpInterface=''
                GuanliIP.append(SnmpInterface)
        ExcelEverySheetData = {
            '主机名': Zhujiming,
            '主机IP': ZhujiIP,
            '管理IP': GuanliIP,
            '厂商': Changshang,
            '序列号': Xuliehao,
            '机房': Jifang
        }
        df=pd.DataFrame(ExcelEverySheetData)
        if GroupName.find('/')>-1:
            GroupName=GroupName.replace('/','-')
        if GroupName.find(':')>-1:
            GroupName=GroupName.replace(':','-')
        print(GroupName)
        sf=StyleFrame(df)
        sf.to_excel(exwriter,sheet_name=GroupName)
    exwriter.save()
    exwriter.close()

def ReturnBasicInfoFromGroupId(groupid:str,ExcelContent:dict):
    '''
    :param groupid: zabbix的groupid，string类型
    :param ExcelContent: dict类型，总体需要导入到Excel里的数据的一个集合。
    :return: ExcelContent
    '''
    hosts = zapi.host.get(groupids=groupid, output='extend', withInventory=1,
                          selectInventory=['vendor', 'serialno_b', 'location'])
    ###count用来计算是ExcelContent里第几个元素需要进行数据更新
    count = 0
    for i in ExcelContent:
        if str(i['groupid']) == str(groupid):
            GroupInfo=i
            for host in hosts:
                ####generate hostinterface info
                hostinterfaces_json = {}
                hostinterfaces = zapi.hostinterface.get(hostids=host['hostid'])
                for hostinterface in hostinterfaces:
                    hostinterfaces_json[(hostinterface['type'])] = hostinterface['ip']
                ####
                GroupInfo['content'].append({
                    'hostid': (host['hostid']),
                    'hostname': (host['host']),
                    ##统计资产清单
                    'inventory': host['inventory'],
                    'interfaces':[hostinterfaces_json]
                })

            ExcelContent[count]=GroupInfo

        count = count + 1

    return ExcelContent


if __name__ == '__main__':
    ExcelContent=[]
    parse = argparse.ArgumentParser("")
    parse.add_argument("username")
    parse.add_argument("password")
    args = parse.parse_args()
    url = "http://url.com"  # 这里填写url
    zapi = ZabbixAPI(server=url)
    warnings.filterwarnings('ignore')
    zapi.login(user=args.username, password=args.password)
    #host_groups = zapi.hostgroup.get(real_hosts=1, with_monitored_items=1, excludeSearch=1, filter={"flags": "0"},search={"name": ["网络设备", "Zabbix server", "Hypervisors", "Virtual machines","Discover VMware VMs"]})
    host_groups = zapi.hostgroup.get( real_hosts=1, with_monitored_items=1,filter={"flags": "0"},excludeSearch=1,search={"name": [ "Hypervisors", "Virtual machines"]})

    for host_group in host_groups:
        groupid=host_group['groupid']
        groupname=host_group['name']
        ExcelContent.append({'groupid':groupid,
                             'groupname':groupname,
                             'content':[]
                             })


    for EachExcelContent in ExcelContent:
        ExcelContent = ReturnBasicInfoFromGroupId(EachExcelContent['groupid'], ExcelContent)

    #with open('raw.json','w') as f:
        #f.write(str(ExcelContent))
    WriteRawdataToExcel(ExcelContent,'Zabbix主机信息表.xlsx')

