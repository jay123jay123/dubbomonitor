import  time
import threading
Nowstamp = time.time() - 120
date = time.strftime("%H:%M", time.localtime(Nowstamp))
today = time.strftime("%Y%m%d", time.localtime(Nowstamp))
tmpdate = time.strftime("%Y-%m-%d %H:%M:00", time.localtime(Nowstamp))
timeArray = time.strptime(tmpdate, "%Y-%m-%d %H:%M:%S")
timestamp = int(time.mktime(timeArray))

def aaa(a):
    str = "statistics_openApi-mobile-consumer_20171031|net.xuele.circle.service.VoteService|vote" + a
    print list(str.split("|"))
    print time.time()

for i in range(5):
    t = threading.Thread(target=aaa,args=("aaaaaaa",))
    t.start()



