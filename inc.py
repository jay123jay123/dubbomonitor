#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
import  pymysql
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

def Mysql():
    conn = pymysql.connect(host='192.168.8.110', port=3306, user='root', passwd='xuele123', db='dubbomonitor',charset='utf8')
    cursor = conn.cursor()
    return  conn,cursor

def CloseMysql(conn,cursor):
    cursor.close()
    conn.close()

def MinTime(seconds = 120):
    Nowstamp = time.time() - seconds
    date = time.strftime("%H:%M", time.localtime(Nowstamp))
    today = time.strftime("%Y%m%d", time.localtime(Nowstamp))
    tmpdate = time.strftime("%Y-%m-%d %H:%M:00", time.localtime(Nowstamp))
    timeArray = time.strptime(tmpdate, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return date, today ,timestamp

def GetApplicationSql():
    sql = "select name from application order by type desc"
    return sql

def GetModules():
    Modules = []
    conn,cursor = Mysql()
    cursor.execute(GetApplicationSql())
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        Modules.append(row[0])
    CloseMysql(conn,cursor)
    return  Modules

def AllMethodSql(tablename):
    sql = "select serviceInterface  , method  from `%s` group by serviceInterface  , method" %(tablename)
    return  sql

def AllMethod(tablename):
    allmethodlist = []
    conn, cursor = Mysql()
    cursor.execute(AllMethodSql(tablename))
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        tmplist = []
        tmplist.append(row[0])
        tmplist.append(row[1])
        allmethodlist.append(tmplist)
    CloseMysql(conn,cursor)
    return  allmethodlist

def AlarmWeixin(str):
    os.system("curl -X POST -d 'touser=dubboMonitor&content='%s http://192.168.8.253/sendchat.php >/dev/null 2>&1" % (str))
    return 0