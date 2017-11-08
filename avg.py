#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')


def MinAvgSql(tablename,timestamp):
    sql = "select serviceInterface  , method  , AVG(elapsed) from `%s` where timestamp  < %s *1000  and  timestamp > (%s - 60 )*1000  group by serviceInterface  , method" % (tablename, timestamp, timestamp)
    return  sql


def CreateTableSql(tablename):
    sql = "create table `%s` (id int NOT NULL AUTO_INCREMENT,timestamp varchar(16) NOT NULL , serviceInterface varchar(128) NOT NULL , method varchar(128) NOT NULL , elapsed int(8) DEFAULT '0' , failureCount  int(8) DEFAULT '0' , successCount  int(8) DEFAULT '0'  ,PRIMARY KEY (`id`), KEY `time-index` (`timestamp`),  UNIQUE KEY idx (serviceInterface,method,timestamp))" %(tablename)
    return sql

def InsertTableSql(tablename,date,serviceInterface,method,elapsed):
    sql = "insert into `%s` (timestamp,serviceInterface,method,elapsed) values('%s','%s','%s','%s')"  %(tablename,date,serviceInterface,method,elapsed)
    return sql


def CreateTable(tablename):
    conn, cursor = Mysql()
    cursor.execute(CreateTableSql(tablename))
    conn.commit()
    CloseMysql(conn, cursor)

def DropTable(tablename):
    conn, cursor = Mysql()
    cursor.execute("drop table `%s`" %(tablename))
    conn.commit()
    CloseMysql(conn, cursor)

def CheckTable(tablename):
    conn, cursor = Mysql()
    try:
        cursor.execute("select count(1) from `%s` limit 1" %(tablename))
    except:
        CreateTable(tablename)
    conn.commit()
    CloseMysql(conn, cursor)


def InsertTable(tablename,date,serviceInterface,method,elapsed):
    conn, cursor = Mysql()
    cursor.execute(InsertTableSql(tablename,date,serviceInterface,method,elapsed))
    conn.commit()
    CloseMysql(conn, cursor)


def MinAvg(tablename,timestamp):
    melist = []
    conn, cursor = Mysql()
    cursor.execute(MinAvgSql(tablename,timestamp))
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        templist = []
        templist.append(row[0])
        templist.append(row[1])
        templist.append(row[2])
        melist.append(templist)
    CloseMysql(conn, cursor)
    return melist


def MergeAvg(module,allmethodlist,melist):
    alltmplist = []
    metmplist = []
    for a in allmethodlist:
        alltmplist.append('%s|%s|%s' %(module,a[0],a[1]))
    for m in melist:
        metmplist.append('%s|%s|%s' %(module,m[0],m[1]))

    for k in alltmplist:
        if k in metmplist:
            pass
        else:
            k = k + '|0'
            new = list(k.split("|"))
            melist.append([new[1],new[2],new[3]])

    return melist

def loop(module,date,today,timestamp):
    st = "statistics_%s_%s" %(module,today)
    avgt = "avg_%s_%s" %(module,today)
    rt = "result_%s" %(module)

    if date == "00:00":
        #DropTable(avgt)
        CreateTable(avgt)

    allmethodlist = AllMethod(rt)
    melist = MinAvg(st, timestamp)
    melist2 = MergeAvg(module,allmethodlist,melist)

    for c in melist2:
        print avgt, date, c[0], c[1], c[2]
        CheckTable(avgt)
        InsertTable(avgt, date, c[0], c[1], c[2])


def main():
    date,today,timestamp = MinTime()
    Modules = GetModules()
    for m in Modules:
        loop(m,date,today,timestamp)





if __name__ == '__main__':
    main()



