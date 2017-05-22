# -*- coding:utf-8 -*-
from Lib import isAlive,getHtml,getHtmlP,hotList
from selenium import webdriver
import logging
import time,datetime,urllib,requests,re,threading,random
from Queue import Queue

import MySQLdb as mdb
from mysql.connector import pooling
proxyUrl=['http://www.kuaidaili.com/free/','http://www.xicidaili.com/nn/']
#Q1,Q2 for Proxy
Q1=Queue()
Q2=Queue()
#Q3,Q4 for UK
Q3=Queue()
Q4=Queue()
Q5=Queue()
global proxyList
proxyList=[0]*10


def get_logger():
    '''
    logger = logging.getLogger("threading_example")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("threading.log")
    fmt = "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    '''
    logging.basicConfig(level = logging.INFO,format = "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s")
    
    logger = logging.getLogger("__name__")
    return logger


'''
#####################################################


####################################################
'''
def proxySource(Q1):
    global proxyUrl
    while True:
        #if datetime.datetime.now().minute%10==0 and datetime.datetime.now().second==0:
        if(Q1.qsize()<200):
            '''
            XiCiDaiLi
            '''
            url2=proxyUrl[1]
            ipPort2=[]
            html=getHtml(url2)
            res=re.findall(r'<tr class="odd">(.*?)<td>(.*?)</td>(.*?)</td>',html,re.S)
            for i in range(len(res)):
                tempIP2=res[i][1]
                temp=res[i][2].strip()
                tempPort2=temp[4:]
                ipPort2=(tempIP2+':'+tempPort2)
                Q1.put(str(ipPort2))
                
            '''
            KuaiDaiLi
            '''
            url1P1=proxyUrl[0]
            pageNum=0
            #国内高匿：inha   国内普通：intr   国外高匿：outha   国外普通：outtr
            proxyType=['inha','intr','outha','outtr']
            maxNum=4
            ipList=[]
            portList=[]
            driver = webdriver.PhantomJS(executable_path='C:/PyProj/DRIVER/phantomjs/bin/phantomjs')
            while pageNum<=maxNum:
                pageNum+=1
                url1=url1P1+proxyType[0]+'/'+str(pageNum)
                driver.get(url1)
                html=driver.page_source
                time.sleep(1)
                tempIP1=re.findall(r'<td data-title="IP">(.*?)</td>',html,re.S)
                tempPort1=re.findall(r'<td data-title="PORT">(.*?)</td>',html,re.S)
                ipList+=tempIP1
                portList+=tempPort1
            driver.quit()
            for i in range(len(ipList)):
                ipPort1=(ipList[i]+':'+portList[i])
                Q1.put(str(ipPort1))
            time.sleep(600)

def proxyCheck(Q1,Q2,logger):
    while True:
        if(not Q1.empty()):
            ipPort=Q1.get()
            if isAlive(ipPort):
                #print ipPort+' Works'
                logger.debug('{} works'.format(ipPort))
                Q2.put(ipPort)

def queueSize(Q1,Q2,Q3,Q4,Q5,logger):
    global proxyList
    while True:
        if(datetime.datetime.now().second==30):
            '''
            print 'Q1 size : '+str(Q1.qsize())
            print 'Q2 size : '+str(Q2.qsize())     
            print 'Q3 size : '+str(Q3.qsize())
            print 'Q4 size : '+str(Q4.qsize())  
            print 'Q5 size : '+str(Q5.qsize())
            '''
            logger.info('Q1 Size：{}; Q2 Size：{}; Q3 Size：{}; Q4 Size：{}; Q5 Size：{};'.format(Q1.qsize(),Q2.qsize(),Q3.qsize(),Q4.qsize(),Q5.qsize(),))
            time.sleep(5)
            temp=[]
            while (not Q2.empty()):
                item=Q2.get()
                if not item in proxyList:
                    temp.append(item)
            k=len(temp)
            if k!=0:
                proxyList=temp+proxyList[:-k]
                #print 'proxyList: '
                #print proxyList  
                logger.info('proxyList：{}'.format(proxyList))
def getHtmlE(url):            
    global proxyList
    tempList=[]
    if proxyList[9]!=0:
        tempList=random.sample(proxyList,3)
        #print 'random select'
    elif proxyList[2]!=0:
        tempList=proxyList[:3]
        #print 'first three elements'
    else:
        tempList=[]
        #print 'no proxy available now'
    if tempList!=[]:
        for i in tempList:
            html=getHtmlP(url,i)
            if html.find('SoBaiduPan')!=-1:
                #print '代理搜索成功'
                logger.debug('代理搜索成功')
                return html
    html=getHtml(url)
    #print '使用本地IP'
    logger.debug('使用本地IP')
    return html
         
def S_Sobaidupan(rawWord,MD5Key):
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    
    ukList=[]
    pageNum=0
    
    url1='http://www.sobaidupan.com/search.asp?r=0&wd='
    url2='&p=&page=' #followed by page number
    #url=url1+keyWord
    reg=r'user-(.*?)-1'
    regExp=re.compile(reg)
    #html=getHtmlE(url)
    #tempList=re.findall(regExp,html)
    #ukList=ukList+tempList
    #while(html.find("下一页")!=-1):
    while(pageNum<10):
        pageNum=pageNum+1
        url=url1+keyWord+url2+str(pageNum)+'&so_md5key='+MD5Key
        #print url
        html=getHtmlE(url)
        tempList=re.findall(regExp,html)
        ukList=ukList+tempList
    setList=set(ukList)
    resList=list(setList)
    return resList

'''
#############################################################


#############################################################
'''

def getTitle(Q5,iniNum):
    #for tag in Tags:
    hotTitle=hotList()
    for i in hotTitle:
        Q5.put(i)
    startNum=iniNum
    paceNum=500
    time.sleep(50)
    while True:
        if(Q5.empty()):
            cur3=con3.cursor()
            cur3.execute('select * from titlelist where id>=%s and id<%s',[startNum,(startNum+paceNum)])
            items=cur3.fetchall()
            cur3.close()
            for i in items:
                Q5.put(i[1])
            startNum+=paceNum
         
'''
def getTitle(Q5):
    #for tag in Tags:
    startNum=45954
    paceNum=500
    while True:
        if(Q5.empty()):
            cur3=con3.cursor()
            cur3.execute('select * from titlelist where id>=%s and id<%s',[startNum,(startNum+paceNum)])
            items=cur3.fetchall()
            cur3.close()
            for i in items:
                Q5.put(i[1])
            startNum+=paceNum
'''            
def getUk(Q5,Q3,logger,MD5Key):
    while True:
        title=Q5.get()
        #print title
        logger.info('Now is searching: {}'.format(title))
        ukList=S_Sobaidupan(title,MD5Key)
        #print ukList
        logger.info('ukList：{}'.format(ukList))
        for j in ukList:
            Q3.put(j)
        time.sleep(5)

def newUK(Q3,Q4,logger):
    while True:
        cur2 = con2.cursor()
        newUkNum=0
        while(Q3.empty()!=True):
            uk=Q3.get()
            cur2.execute('select uk from uklist where uk=%s',(uk,))
            res=cur2.fetchall()
            if res==[]: #判断是否已经收录此uk
                newUkNum+=1
                Q4.put(uk)
                #print 'New uk : '+uk
        
        cur2.close()
        #print '此次验证新UK : '+str(newUkNum)
        logger.info('此次验证新UK ：{}'.format(str(newUkNum)))
        time.sleep(30)
            
def writeMySQL(Q4,logger):
    num=0
    while True:
        cur1 = con1.cursor()
        while(not Q4.empty()):
            uk=Q4.get()
            cur1.execute('insert into uklist(uk) values(%s)',(uk,))
            num=num+1
        cur1.close()
        con1.commit()
        
        #print '当前新UK数 ：'+str(num)
        logger.info('当前新UK数 ：{}'.format(str(num)))
        time.sleep(60)


if __name__=='__main__':
    
    iniNum=120526
    url='http://www.sobaidupan.com/'
    html=getHtml(url)
    startP=html.find('name="so_md5key" value="')
    MD5Key=html[startP+24:startP+56]
    print MD5Key
    #MD5Key='5b18d3fb3018f995bc0618ce99b9c231'
    
    ######################################
    dbconfig = {
      "database": "baiduyun",
      "user":     "root",
      "password":"123456"
    }
    conPool=pooling.MySQLConnectionPool(pool_name = "mypool",pool_size = 3,**dbconfig)
    con1=conPool.get_connection()
    con2=conPool.get_connection()
    con3=conPool.get_connection()
    '''
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    '''
    threads=[]
    
    logger=get_logger()
    thread_names=['proxySource','proxyCheck','queueSize','getTitle','newUK','writeMySQL','getUk-1','getUk-2']
    
    t1=threading.Thread(target=proxySource,args=(Q1,))
    threads.append(t1)

    t2=threading.Thread(target=proxyCheck,name = thread_names[0],args=(Q1,Q2,logger,))
    threads.append(t2)
    
    t3=threading.Thread(target=proxyCheck,name = thread_names[1],args=(Q1,Q2,logger,))
    threads.append(t3)
    
    t4=threading.Thread(target=queueSize,name = thread_names[2],args=(Q1,Q2,Q3,Q4,Q5,logger,))
    threads.append(t4) 
    
    t5=threading.Thread(target=getTitle,args=(Q5,iniNum,))
    threads.append(t5)
    
    t6=threading.Thread(target=newUK,args=(Q3,Q4,logger,))
    threads.append(t6)
    
    t7=threading.Thread(target=writeMySQL,args=(Q4,logger,))
    threads.append(t7)
    
    t8=threading.Thread(target=getUk,args=(Q5,Q3,logger,MD5Key,))
    threads.append(t8)
    
    t9=threading.Thread(target=getUk,args=(Q5,Q3,logger,MD5Key,))
    threads.append(t9)

    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()

    
