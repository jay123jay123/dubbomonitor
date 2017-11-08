import  time
import  MySQLdb
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

def Mysql():
    conn = MySQLdb.connect(host='192.168.8.253', port=3306, user='root', passwd='xuele123', db='dubbomonitor',charset='utf8')
    cursor = conn.cursor()
    return  conn,cursor

def CloseMysql(conn,cursor):
    cursor.close()
    conn.close()

def MinTime():
    Nowstamp = time.time() - 120
    date = time.strftime("%H:%M", time.localtime(Nowstamp))
    today = time.strftime("%Y%m%d", time.localtime(Nowstamp))
    tmpdate = time.strftime("%Y-%m-%d %H:%M:00", time.localtime(Nowstamp))
    timeArray = time.strptime(tmpdate, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return date, today ,timestamp

def GetApplicationSql():
    sql = "select name from application"
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

def MinAvgSql(tablename,timestamp):
    sql = "select serviceInterface  , method  , AVG(elapsed) from `%s` where timestamp  < %s *1000  and  timestamp > (%s - 60 )*1000  group by serviceInterface  , method" % (tablename, timestamp, timestamp)
    return  sql

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

def CreateTableSql(tablename):
    sql = "create table `%s` (id int NOT NULL AUTO_INCREMENT,timestamp varchar(16) NOT NULL , serviceInterface varchar(16) NOT NULL , method varchar(16) NOT NULL , elapsed int(8) DEFAULT '0' , failureCount  int(8) DEFAULT '0' ,PRIMARY KEY (`id`), KEY `time-index` (`timestamp`),  KEY `method-index` (`method`), KEY `service-index` (`serviceInterface`) )" %(tablename)
    return sql

def InsertTableSql(tablename,date,serviceInterface,method,elapsed):
    sql = "insert into `%s` (timestamp,serviceInterface,method,elapsed) values('%s','%s','%s','%s') %(tablename,date,serviceInterface,method,elapsed)"
    return sql


def CreateTable(tablename):
    conn, cursor = Mysql()
    cursor.execute(CreateTableSql(tablename))
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




def main():
    date,today,timestamp = MinTime()
    Modules = GetModules()
    if date == "00:00"
        CreateTable(tablename)

    allmethodlist = AllMethod(tablename)
    melist = MinAvg(tablename, timestamp)
    melist2 = MergeAvg(module,allmethodlist,melist)

    for c in melist2:
        InsertTable(tablename, date, c[0], c[1], c[2])



if __name__ == '__main__':
    main()



