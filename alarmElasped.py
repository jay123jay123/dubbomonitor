#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

#加区间报警

def AlarmRange(number):
    if number <= 30:
        return 100,10
    elif number <= 100 and number > 30:
        return  80,5
    elif number <= 500 and number > 100:
        return  50,5
    elif number <= 1000 and number > 500:
        return  30,3
    elif number <= 2000 and number > 1000:
        return  20,3
    else:
        return 10,1

def InsertAlarmSql(module,serviceInterface,method,percentage , totaltime ):
    sql = "insert into alarm(module,serviceInterface,method,percentage,totaltime , num) values('%s','%s','%s','%s','%s','1')"  %(module,serviceInterface,method,percentage, totaltime )
    return  sql

def UpdateAlarmSql(module,serviceInterface,method,percentage , totaltime ):
    sql = "update alarm set num = num + 1 , percentage = percentage + %s , totaltime = totaltime + %s where module = '%s' and serviceInterface = '%s' and method = '%s' " %(percentage , totaltime ,module,serviceInterface,method)
    return  sql

def ResetAlarmSql(module,serviceInterface,method):
    sql = "update alarm set num = 0 , percentage = 0 , totaltime = 0 where module = '%s' and serviceInterface = '%s' and method = '%s'" %(module,serviceInterface,method)
    print sql
    return  sql

def CompareAlarmSql(module):
    sql = "select module,serviceInterface,method from alarm where module = '%s' and  num > 0 " %(module)
    return  sql

def SelectAlarmSql(module,serviceInterface,method):
    sql = "select num,percentage,totaltime from alarm where module = '%s' and serviceInterface = '%s' and method = '%s' " %(module,serviceInterface,method)
    return  sql


def DaysAvgSql(tablename,date):
    sql = "select serviceInterface  , method  , elapsed from `%s` where timestamp = '%s'  group by serviceInterface  , method" % (tablename, date)
    #print sql
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
        tst = TodayAvg(todayavgtable,date,st[0],st[1])   #日均值


        if tst == 0:
            continue
        if st[2] == 0:
            #st[2] = 1
            continue

        if st[2] <= 10:
            continue

        sper,count = AlarmRange(st[2])

        if ( tst - st[2] )  <= 0:
            continue
        else:
            percentage =  ( tst - st[2] )  * 100 / st[2]

        if percentage > sper:
            print module, st[0], st[1], percentage,count , st[2]
            #alarm.append([module,st[0],st[1],percentage,count , st[2]])  #count是持续几次告警，st[2] 是 7日均线
            alarm.append([module, st[0], st[1], percentage, tst])

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

def CompareAlarm(alarm,date):
    conn, cursor = Mysql()
    for a in alarm:
        cursor.execute(SelectAlarmSql(a[0],a[1],a[2]))
        res = cursor.fetchone()   #res[0] : num   ;  res[1] : percentage ; res[2] : totaltime
        if res == None:
            cursor.execute(InsertAlarmSql(a[0],a[1],a[2],a[3],a[4]))
            conn.commit()
            continue
        else:
            cursor.execute(UpdateAlarmSql(a[0],a[1],a[2],a[3],a[4]))
            conn.commit()
        print res[0] , res[1] , res[2] , a[0] , a[1] , a[2]
        if res[0] == 0:
            cursor.execute(ResetAlarmSql(a[0],a[1],a[2]))
            conn.commit
            continue
        avgE =  res[2] / res[0]
        percentage =  res[1] / res[0]
        daystime = avgE / ( percentage + 1 )
        sper, count = AlarmRange(daystime)

        if int(res[0]) >= count:
            cursor.execute(ResetAlarmSql(a[0],a[1],a[2]))
            conn.commit()
            if percentage >= 50:
                str = '严重:[%s]%s里的%s的%s方法调用\(平均%sms上浮%s%%\)%s次' %(date,a[0],a[1],a[2],avgE,percentage,res[0])
            else:
                str = '告警:[%s]%s里的%s的%s方法调用\(平均%sms上浮%s%%\)%s次' %(date,a[0],a[1],a[2],avgE,percentage,res[0])
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



