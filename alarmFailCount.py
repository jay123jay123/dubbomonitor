#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

#加区间报警
#加failureCount

def AlarmRangeFail(number):
    if number <= 10:
        return 30
    elif number <= 1000 and number > 10:
        return  10
    elif number <= 3000 and number > 1000:
        return  5
    else:
        return 1

def SelectApplicationSql(module,today):
    sql = "select sum(failureCount + successCount) as num from  `avg_%s_%s`" % (module, today)
    return  sql

def UpdateApplicationSql(num,module):
    sql = "update application set num =  %s where name = '%s'" %(num,module)
    #print sql
    return  sql

def InsertAlarmFailSql(module,serviceInterface,method,percentage,failureCount):
    sql = "insert into alarmfailcount(module,serviceInterface,method,percentage,num,failureCount) values('%s','%s','%s','%s','1','%s')"  %(module,serviceInterface,method,percentage,failureCount)
    return  sql

def UpdateAlarmFailSql(module,serviceInterface,method,percentage,failureCount):
    sql = "update alarmfailcount set num = num + 1 , percentage = percentage + %s  , failureCount = failureCount + %s where module = '%s' and serviceInterface = '%s' and method = '%s' " %(percentage,failureCount,module,serviceInterface,method)
    return  sql

def ResetAlarmFailSql(module,serviceInterface,method):
    sql = "update alarmfailcount  set num = 0 , percentage = 0 , failureCount = 0 where module = '%s' and serviceInterface = '%s' and method = '%s'" %(module,serviceInterface,method)
    return  sql

def CompareAlarmFailSql(module):
    sql = "select module,serviceInterface,method from alarmfailcount  where module = '%s' and  num > 0 " %(module)
    return  sql

def SelectAlarmFailSql(module,serviceInterface,method):
    sql = "select num,percentage,failureCount from alarmfailcount where module = '%s' and serviceInterface = '%s' and method = '%s' " %(module,serviceInterface,method)
    return  sql


def DaysAvgFailSql(tablename,date):
    sql = "select serviceInterface  , method , failureCount , successCount from `%s` where timestamp = '%s'  group by serviceInterface  , method" % (tablename, date)
    #print sql
    return  sql

def TodayAvgFailSql(tablename,date,serviceInterface,method):
    sql = "select failureCount,successCount from `%s` where serviceInterface = '%s' and method = '%s' and timestamp = '%s' order by id desc limit 1" % (tablename, serviceInterface, method ,date)
    return  sql

def UpdateApplication(module,today):
    conn, cursor = Mysql()
    cursor.execute(SelectApplicationSql(module,today))
    res = cursor.fetchone()
    #print res[0]
    cursor.execute(UpdateApplicationSql(res[0],module))
    conn.commit()
    CloseMysql(conn, cursor)

def DaysAvgFail(tablename,date):
    dayslist = []
    conn, cursor = Mysql()
    cursor.execute(DaysAvgFailSql(tablename,date))
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        templist = []
        templist.append(row[0])
        templist.append(row[1])
        templist.append(row[2])  #failureCount
        templist.append(row[3])  #successCount
        dayslist.append(templist)
    CloseMysql(conn, cursor)
    return dayslist

def TodayAvgFail(tablename,date,serviceInterface,method):
    conn, cursor = Mysql()
    cursor.execute(TodayAvgFailSql(tablename,date,serviceInterface,method))
    res = cursor.fetchone()
    if res == None:
        return 0
    CloseMysql(conn, cursor)
    return res[0] , res[1]

def CompareAvgFail(module, date, today ,timestamp):
    daysavgtable = "result_%s" %(module)
    todayavgtable = "avg_%s_%s" %(module,today)
    alarm = []

    dayslist = DaysAvgFail(daysavgtable,date)   #获取接口和方法列表

    for st in dayslist:
        percentage = 0
        fnum,snum = TodayAvgFail(todayavgtable,date,st[0],st[1])


        if fnum == 0:
            continue
        #if st[2] == 0:
        #    continue

        tnum = fnum + snum
        sper = AlarmRangeFail(tnum)
        percentage = fum * 100 / tnum
        dayspercentage = st[2] * 100 / ( st[2] + st[3] )
        diffper = percentage - dayspercentage

        if diffper <= 0:
            continue
        else:
            if diffper > 5:
                alarm.append([module,st[0],st[1],percentage,fnum])
    print alarm
    return alarm

def ResetAlarmFail(alarm):
    if len(alarm) == 0:
        return 0

    templist = []
    for key in alarm:
        templist.append('%s%s%s' % (key[0], key[1], key[2]))

    conn, cursor = Mysql()

    cursor.execute(CompareAlarmFailSql(alarm[0][0]))
    res = cursor.fetchall()
    if res == None:
        return 0
    else:
        for row in res:
            s = '%s%s%s' % (row[0], row[1], row[2])
            if s not in templist:
                cursor.execute(ResetAlarmFailSql(row[0],row[1],row[2]))
                conn.commit()

    CloseMysql(conn, cursor)
    return 0

def AlarmWeixin(str):
    os.system("curl -X POST -d 'touser=dubboMonitor&content='%s http://192.168.8.253/sendchat.php >/dev/null 2>&1" % (str))
    return 0;

def CompareAlarmFail(alarm,date):
    conn, cursor = Mysql()
    for a in alarm:
        cursor.execute(SelectAlarmFailSql(a[0],a[1],a[2]))
        res = cursor.fetchone();
        if res == None:
            cursor.execute(InsertAlarmFailSql(a[0],a[1],a[2],a[3],a[4]))
            conn.commit()
            continue
        else:
            cursor.execute(UpdateAlarmFailSql(a[0],a[1],a[2],a[3],a[4]))
            conn.commit()

        if int(res[0]) >= 5:
            percentage = res[1] / res[0]
            cursor.execute(ResetAlarmFailSql(a[0],a[1],a[2]))
            conn.commit()
            if percentage >= 50:
                str = '严重:[%s]%s里的%s的%s方法调用失败\(浮动%s%%\)5次' %(date,a[0],a[1],a[2],percentage)
            else:
                str = '告警:[%s]%s里的%s的%s方法调用失败5次上浮平均%s%%' %(date,a[0],a[1],a[2],percentage)
            print str

            AlarmWeixin(str)

    CloseMysql(conn, cursor)




def loop(module,date,today,timestamp):
    alarm = CompareAvgFail(module, date, today, timestamp)
    ResetAlarmFail(alarm)
    CompareAlarmFail(alarm, date)




def main():
    date,today,timestamp = MinTime(300)
    Modules = GetModules()

    for m in Modules:
        try:
            UpdateApplication(m, today)
        except:
            pass

        #print m , date , today, timestamp
        loop(m , date , today, timestamp)



if __name__ == '__main__':
    main()



