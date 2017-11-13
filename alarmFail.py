#!/usr/bin/env python
# -*- coding:utf-8 -*-
import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

#加区间报警
#加failure


def SelectApplicationSql(module,today):
    sql = "select sum(failureCount + successCount) as num from  `avg_%s_%s`" % (module, today)
    return  sql

def UpdateApplicationSql(num,module):
    sql = "update application set num =  %s where name = '%s'" %(num,module)
    #print sql
    return  sql

def TodayAvgFailSql(module,date,today):
    sql = "select serviceInterface,method,failureCount,successCount from `avg_%s_%s` where failureCount > 0 and timestamp = '%s' order by id desc limit 1" % (module,today, date)
    return  sql

def UpdateApplication(module,today):
    conn, cursor = Mysql()
    cursor.execute(SelectApplicationSql(module,today))
    res = cursor.fetchone()
    #print res[0]
    cursor.execute(UpdateApplicationSql(res[0],module))
    conn.commit()
    CloseMysql(conn, cursor)

def TodayAvgFail(module,date,today):
    conn, cursor = Mysql()
    cursor.execute(TodayAvgFailSql(module,date,today))
    res = cursor.fetchall()
    if res == None:
        return 0
    for row in res:
        serviceInterface, method , failureCount , successCount =  row[0] , row[1] , row[2] , row[3]
        per = failureCount / (failureCount + successCount)  * 100
        print module,serviceInterface, method,failureCount , successCount , per
        if failureCount > 30:
            str = '严重:[%s]%s里的%s的%s方法调用失败%s%%' % (date, module, serviceInterface, method, per)
        else:
            if per > 50:
                str = '严重:[%s]%s里的%s的%s方法调用失败%s次' % (date, module, serviceInterface, method, failureCount)

            else:
                str = '告警:[%s]%s里的%s的%s方法调用失败%s%%' % (date, module, serviceInterface, method, per)





        AlarmWeixin(str)

    CloseMysql(conn, cursor)
    return 0







def loop(module,date,today):
    TodayAvgFail(module, date, today)




def main():
    date,today,timestamp = MinTime(300)
    Modules = GetModules()

    for m in Modules:
        try:
            UpdateApplication(m, today)
        except:
            pass

        #print m , date , today, timestamp
        loop(m , date , today)



if __name__ == '__main__':
    main()



