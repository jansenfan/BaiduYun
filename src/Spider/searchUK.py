# -*- coding:utf-8 -*-
from Lib import isAlive,getHtml,getHtmlP

from selenium import webdriver
import time,datetime,urllib,requests,re,threading,random
from Queue import Queue

import MySQLdb as mdb
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

def proxyCheck(Q1,Q2):
    while True:
        if(not Q1.empty()):
            ipPort=Q1.get()
            if isAlive(ipPort):
                print ipPort+' Works'
                Q2.put(ipPort)

def queueSize(Q1,Q2,Q3,Q4,Q5):
    global proxyList
    while True:
        if(datetime.datetime.now().second==30):
            print 'Q1 size : '+str(Q1.qsize())
            print 'Q2 size : '+str(Q2.qsize())     
            print 'Q3 size : '+str(Q3.qsize())
            print 'Q4 size : '+str(Q4.qsize())  
            print 'Q5 size : '+str(Q5.qsize())
            time.sleep(5)
            temp=[]
            while (not Q2.empty()):
                item=Q2.get()
                if not item in proxyList:
                    temp.append(item)
            k=len(temp)
            if k!=0:
                proxyList=temp+proxyList[:-k]
                print 'proxyList: '
                print proxyList  
                
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
                print '代理搜索成功'
                return html
    html=getHtml(url)
    print '使用本地IP'
    return html
         
def S_Sobaidupan(rawWord):
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    
    ukList=[]
    pageNum=0
    
    url1='http://www.sobaidupan.com/search.asp?r=0&wd='
    url2='&p=&page=' #followed by page number
    url=url1+keyWord
    reg=r'user-(.*?)-1'
    regExp=re.compile(reg)
    #html=getHtmlE(url)
    #tempList=re.findall(regExp,html)
    #ukList=ukList+tempList
    #while(html.find("下一页")!=-1):
    while(pageNum<10):
        pageNum=pageNum+1
        url=url1+keyWord+url2+str(pageNum)
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


def getTitle(Q5):
    #for tag in Tags:
    startNum=43930
    paceNum=500
    time.sleep(50)
    while True:
        if(Q5.empty()):
            cur=con.cursor()
            cur.execute('select * from titlelist where id>=%s and id<%s',[startNum,(startNum+paceNum)])
            items=cur.fetchall()
            cur.close()
            for i in items:
                Q5.put(i[1])
            startNum+=paceNum
            
def getUk(Q5,Q3):
    while True:
        title=Q5.get()
        print title
        ukList=S_Sobaidupan(title)
        print ukList
        for j in ukList:
            Q3.put(j)
        time.sleep(5)

def newUK(Q3,Q4):
    while True:
        if(datetime.datetime.now().minute%3==0):
            cur = con.cursor()
            newUkNum=0
            while(Q3.empty()!=True):
                uk=Q3.get()
                if cur.execute('select uk from uklist where uk=%s',uk)==0: #判断是否已经收录此uk
                    newUkNum+=1
                    Q4.put(uk)
                    #print 'New uk : '+uk
            
            cur.close()
            print '此次验证新UK'+str(newUkNum)
            time.sleep(30)
            
def writeMySQL(Q4):
    num=0
    while True:
        if(datetime.datetime.now().minute%3==2 and datetime.datetime.now().second==30):
            cur = con.cursor()
            while(not Q4.empty()):
                uk=Q4.get()
                cur.execute('insert into uklist(uk) values(%s)',uk)
                num=num+1
            cur.close()
            con.commit()
            
            print '当前新UK数：'+str(num)
            time.sleep(60)


if __name__=='__main__':
   
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    threads=[]
    
    t1=threading.Thread(target=proxySource,args=(Q1,))
    threads.append(t1)

    t2=threading.Thread(target=proxyCheck,args=(Q1,Q2,))
    threads.append(t2)
    
    t3=threading.Thread(target=proxyCheck,args=(Q1,Q2,))
    threads.append(t3)
    
    t4=threading.Thread(target=queueSize,args=(Q1,Q2,Q3,Q4,Q5,))
    threads.append(t4)
    
    t5=threading.Thread(target=getTitle,args=(Q5,))
    threads.append(t5)
    
    t6=threading.Thread(target=newUK,args=(Q3,Q4,))
    threads.append(t6)
    
    t7=threading.Thread(target=writeMySQL,args=(Q4,))
    threads.append(t7)
    
    t8=threading.Thread(target=getUk,args=(Q5,Q3,))
    threads.append(t8)
    
    t9=threading.Thread(target=getUk,args=(Q5,Q3,))
    threads.append(t9)
    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()   

    
