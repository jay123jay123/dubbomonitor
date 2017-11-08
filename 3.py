import  time
from inc import *
import os
import  sys
reload(sys)
sys.setdefaultencoding('utf-8')

def CheckTable(tablename):
    conn, cursor = Mysql()
    try:
        cursor.execute("select count(1) from `%s` limit 1" %(tablename))
    except:
        print "%s not exist" % (tablename)
    print "%s  exist" % (tablename)

    conn.commit()
    CloseMysql(conn, cursor)

CheckTable("avg_cloudtchhome-service-provider_20171101")
