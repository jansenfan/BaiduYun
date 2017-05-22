# -*- coding:utf-8 -*-
from Lib import isAlive,getHtml,getHtmlP,hotList
import MySQLdb as mdb
from selenium import webdriver
import time,datetime,urllib,requests,re,threading,random
from Queue import Queue
proxyUrl=['http://www.kuaidaili.com/free/','http://www.xicidaili.com/nn/']
#Q1,Q2 for Proxy
Q1=Queue()
Q2=Queue()
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
         




def CiTiao():
    cateTag=['96','127','132','154','167','367','389','403','436']
    url1='http://pinyin.sogou.com/dict/cate/index/'
    url2='/default/'
    for cate in cateTag:
        tempUrl=url1+cate
        pageNum=1
        html=getHtml(tempUrl)
        resList=[]
        while html.find('下一页')!=-1:
            pageNum+=1
            res=re.findall(r'<div class="show_content">(.*?)</div>',html,re.S)
            for i in range(len(res)/3):
                temp=res[3*i].split('、')
                resList+=temp
                for j in temp:
                    print j
            url=tempUrl+url2+str(pageNum)
            html=getHtml(url)
        cur=con.cursor()
        num=0
        for item in resList:
            if len(item)<49:
                cur.execute('insert into baiduyun.titlelist(title) values(%s)',item)
            num+=1
        print '此次新增词条数量：'+str(num)
        cur.close()
        con.commit()
            
            
if __name__=='__main__':        
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')          
    CiTiao()
    con.close()  