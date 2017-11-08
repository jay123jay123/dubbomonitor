#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')


def InsertAlarmSql(module,serviceInterface,method,percentage):
    sql = "insert into alarm(module,serviceInterface,method,percentage,num) values('%s','%s','%s','%s','1')"  %(module,serviceInterface,method,percentage)
    return  sql

def UpdateAlarmSql(module,serviceInterface,method,percentage):
    sql = "update alarm set num = num + 1 , percentage = percentage + %s where module = '%s' and serviceInterface = '%s' and method = '%s' " %(percentage,module,serviceInterface,method)
    return  sql

def ResetAlarmSql(module,serviceInterface,method):
    sql = "update alarm set num = 0 , percentage = 0 where module = '%s' and serviceInterface = '%s' and method = '%s'" %(module,serviceInterface,method)
    return  sql

def CompareAlarmSql(module):
    sql = "select module,serviceInterface,method from alarm where module = '%s' and  num > 0 " %(module)
    return  sql

def SelectAlarmSql(module,serviceInterface,method):
    sql = "select num,percentage from alarm where module = '%s' and serviceInterface = '%s' and method = '%s' " %(module,serviceInterface,method)
    return  sql


def DaysAvgSql(tablename,date):
    sql = "select serviceInterface  , method  , elapsed from `%s` where timestamp = '%s'  group by serviceInterface  , method" % (tablename, date)
    print sql
    return  sql

def TodayAvgSql(tablename,date,serviceInterface,method):
    sql = "select elapsed from `%s` where serviceInterface = '%s' and method = '%s' and timestamp = '%s' order by id desc limit 1" % (tablename, serviceInterface, method ,date)
    return  sql

def DaysAvg(tablename,date):
    dayslist = []
    conn, cursor = Mysql()
    cursor.execute(DaysAvgSql(tablename,date))
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        templist = []
        templist.append(row[0])
        templist.append(row[1])
        templist.append(row[2])
        dayslist.append(templist)
    CloseMysql(conn, cursor)
    return dayslist

def TodayAvg(tablename,date,serviceInterface,method):
    conn, cursor = Mysql()
    cursor.execute(TodayAvgSql(tablename,date,serviceInterface,method))
    res = cursor.fetchone()
    if res == None:
        return 0
    CloseMysql(conn, cursor)
    return res[0]

def CompareAvg(module, date, today ,timestamp):
    daysavgtable = "result_%s" %(module)
    todayavgtable = "avg_%s_%s" %(module,today)
    alarm = []

    dayslist = DaysAvg(daysavgtable,date)

    for st in dayslist:
        percentage = 0
        tst = TodayAvg(todayavgtable,date,st[0],st[1])

        if tst == 0:
            continue
        if st[2] == 0:
            #st[2] = 1
            continue

        if st[2] <= 5:
            continue

        if ( tst - st[2] )  <= 0:
            continue
        else:
            percentage =  ( tst - st[2] )  * 100 / st[2]

        if percentage > 10:
            print module, st[0], st[1], percentage
            alarm.append([module,st[0],st[1],percentage])

    return alarm

def ResetAlarm(alarm):
    if len(alarm) == 0:
        return 0

    templist = []
    for key in alarm:
        templist.append('%s%s%s' % (key[0], key[1], key[2]))

    conn, cursor = Mysql()

    cursor.execute(CompareAlarmSql(alarm[0][0]))
    res = cursor.fetchall()
    if res == None:
        return 0
    else:
        for row in res:
            s = '%s%s%s' % (row[0], row[1], row[2])
            if s not in templist:
                cursor.execute(ResetAlarmSql(row[0],row[1],row[2]))
                conn.commit()

    CloseMysql(conn, cursor)
    return 0

def AlarmWeixin(str):
    os.system("curl -X POST -d 'touser=dubboMonitor&content='%s http://192.168.8.253/sendchat.php >/dev/null 2>&1" % (str))
    return 0;

def CompareAlarm(alarm,date):
    conn, cursor = Mysql()
    for a in alarm:
        cursor.execute(SelectAlarmSql(a[0],a[1],a[2]))
        res = cursor.fetchone();
        if res == None:
            cursor.execute(InsertAlarmSql(a[0],a[1],a[2],a[3]))
            conn.commit()
            continue
        else:
            cursor.execute(UpdateAlarmSql(a[0],a[1],a[2],a[3]))
            conn.commit()

        if int(res[0]) >= 5:
            percentage = res[1] / res[0]
            cursor.execute(ResetAlarmSql(a[0],a[1],a[2]))
            conn.commit()
            if percentage >= 30:
                str = '严重:[%s]%s里的%s的%s方法调用超时\(浮动%s%%\)5次' %(date,a[0],a[1],a[2],percentage)
            else:
                str = '告警:[%s]%s里的%s的%s方法调用连续5次上浮平均%s%%' %(date,a[0],a[1],a[2],percentage)
            #print str

            AlarmWeixin(str)

    CloseMysql(conn, cursor)




def loop(module,date,today,timestamp):
    alarm = CompareAvg(module, date, today, timestamp)
    ResetAlarm(alarm)
    CompareAlarm(alarm, date)




def main():
    date,today,timestamp = MinTime(300)
    Modules = GetModules()

    for m in Modules:
        #print m , date , today, timestamp
        loop(m , date , today, timestamp)



if __name__ == '__main__':
    main()



