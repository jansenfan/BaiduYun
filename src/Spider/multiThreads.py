# -*- coding:utf-8 -*-
'''
Created on 2016��11��3��

@author: jansen_fan
'''
import threading,random,time,urllib,urllib2,re,datetime
import MySQLdb as mdb

from Queue import Queue
from random import sample
from bs4 import BeautifulSoup
from Lib import getHtml,Bing,S_Sobaidupan,S_Tebaidu
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def isBDYurl(url):#判断是否pan或者yun格式
    if (str(url).find('pan.baidu.com')!=-1) or (str(url).find('yun.baidu.com')!=-1):
        return 1
    else:
        return 0

def getUk(url):  #根据url，返回相应的uk：字符串格式
    reg=r'uk=(\d+)'
    regExp=re.compile(reg)
    uk=re.findall(regExp,url)
    if len(uk):
        return uk[0]
    else:
        return 'null'

def handlePw(url,pd):#input: password & url; return: uk[string]
    driver = webdriver.PhantomJS(executable_path='C:/PyProj/DRIVER/phantomjs/bin/phantomjs')
    driver.get(url)
    time.sleep(2)
    print '初始地址'+url 
    #print pd
    if pd!='null':
        driver.get(url)
        tempUrl=driver.current_url
        print '识别地址:'+tempUrl
        startUkPos=tempUrl.find('uk=')
        #print startUkPos
        if startUkPos==-1:  # no page exist
            uk='null'
        else:
            uk=tempUrl[startUkPos+3:]  #string 变量
        driver.quit()
        return uk
    else:
        html=driver.page_source
        soup=BeautifulSoup(html,'lxml')
        items=soup.find_all('a',class_='share-person-username')
        if len(items)==0:
            uk='null'
        else:
            startUkPos=items[0].find('home?uk=')
            endUkPos=items[0].find('target')
            uk=items[0][startUkPos:endUkPos]
        driver.quit()
        return uk

def doubanMovieList(tag):
    url1='http://movie.douban.com/tag/'
    url2='?start='
    url3='&type=T'
    
    reg=r'data-total-page="(.+?)">'
    regExp=re.compile(reg)
    regItem=r'title="(.+?)">'
    regExpItem=re.compile(regItem)
    doubanList=[]
    #time.sleep(5)
    Dict={'a':str(tag)}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    urlIni=url1+keyWord
    print urlIni
    html=getHtml(urlIni)
    pageNums=re.findall(regExp,html)
    if len(pageNums)!=0:
        pageNum=int(pageNums[0])
    else:
        pageNum=0
    for j in range(pageNum):
        print str(tag)+'---第'+str(j)+'页'
        url=url1+keyWord+url2+str(20*j)+url3
        htmlItem=getHtml(url)
        items=re.findall(regExpItem,htmlItem)
        doubanList=doubanList+items
        time.sleep(random.randint(1,4))
    return doubanList


'''
def source(Q1):
    #for tag in Tags:
    startNum=36065  
    paceNum=500
    while True:
        cur=con.cursor()
        cur.execute('select * from titlelist where id>=%s and id<%s',[startNum,(startNum+paceNum)])
        items=cur.fetchall()
        cur.close()
        for i in items:
            print i[1]
            urlR=Bing(i[1])
            print urlR
            for j in urlR:
                Q1.put(j)
            time.sleep(random.randint(30,45))
        startNum+=paceNum

           
def findUk(Q1,Q2):
    while True:
        item=Q1.get()
        if isBDYurl(item[0]):
            item[0]=item[0].replace('amp;','')
            uk=getUk(item[0])
            #print '初始地址:'+item[0]
            #print '初始密码:'+item[1]
            if uk=='null':
                continue
                #uk=handlePw(item[0],item[1])
            #print '用户编号:'+uk
            if uk!='null':
                Q2.put(uk)






'''

def source(Q2):
    #for tag in Tags:
    startNum=37068  
    paceNum=500
    num=0
    funcList=[S_Tebaidu,S_Sobaidupan]
    while True:
        cur=con.cursor()
        cur.execute('select * from titlelist where id>=%s and id<%s',[startNum,(startNum+paceNum)])
        items=cur.fetchall()
        cur.close()
        for i in items:
            num=num+1
            sel=num%2
            print i[1]
            urlR=funcList[sel](i[1])
            print urlR
            for j in urlR:
                Q2.put(j)
            time.sleep(random.randint(300,600))
        startNum+=paceNum



def isUkNew(Q2,Q3):
    while True:
        if(datetime.datetime.now().minute%3!=0):
            cur = con.cursor()
            while(Q2.empty()!=True):
                uk=Q2.get()
                if cur.execute('select uk from uklist where uk=%s',uk)==0: #判断是否已经收录此uk
                    cur.execute('insert into uklist(uk) values(%s)',uk)
                    Q3.put(uk)
                    print 'New uk : '+uk
            cur.close()
            time.sleep(30)




def searchHome(Q3,Q4):
    while True:
        uk=Q3.get()
        url=urlHome1+uk+urlHome2
        res=[]
        driver = webdriver.PhantomJS(executable_path='C:/PyProj/DRIVER/phantomjs/bin/phantomjs')
        driver.get(url)
        time.sleep(1)
        pageNum=0
        while(1): 
            pageNum+=1
            print '正在搜索第'+str(pageNum)+'页'
            html=driver.page_source
            soup=BeautifulSoup(html,'lxml')
            tempResult=soup.find_all('a',class_="file-handler")
            for i in tempResult:
                startUrlPos=str(i).find('http:')
                endUrlPos=str(i).find('style=')
                url=str(i)[startUrlPos:endUrlPos-2]
                url.replace('amp;','')
                if len(url)>150:
                    url=url[:145]
                startNamePos=str(i).find('title')+7#加7删除'title='的影响
                endNamePos=str(i).find('unselectable')-2
                name=str(i)[startNamePos:endNamePos]
                if len(name)>100:
                    name='文件名过长'
                res.append([name,url])
            if html.find('page-prev')==-1: #单页，没有下一页
                break
            if html.find('page-next mou-evt disabled')==-1:#判断是否有上一页，-1表示没有   
                try:
                    time.sleep(1)
                    elem=driver.find_element_by_class_name('page-next')
                except NoSuchElementException:
                    print "cant find the element"
                elem.send_keys(Keys.ENTER)
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inifiniteListViewTips")))
                time.sleep(4)  #等待页面加载结束
            else:
                break
        driver.quit()
        for item in res:
            Q4.put([item[0],item[1],uk])

def writeMySQL(Q4):
    num=0
    while True:
        if(datetime.datetime.now().minute%3==0):
            cur = con.cursor()
            while(not Q4.empty()):
                item=Q4.get()
                url=item[1]
                if url.find("http://pan.baidu.com/s/")==-1:
                    continue
                url=url[23:]
                num=num+1
                cur.execute('insert into taglist(title,url,uk) values(%s,%s,%s)',[item[0],url,item[2]])
            cur.close()
            con.commit()
            
            print '当前收录量：'+str(num)
            time.sleep(60)
    
def queueSize(Q1,Q2,Q3,Q4):
    while True:
        print 'Q1 size : '+str(Q1.qsize())
        print 'Q2 size : '+str(Q2.qsize())
        print 'Q3 size : '+str(Q3.qsize())
        print 'Q4 size : '+str(Q4.qsize())
        time.sleep(60)

Q1=Queue()
Q2=Queue()
Q3=Queue()
Q4=Queue()
urlHome1='http://pan.baidu.com/share/home?uk='
urlHome2='#category/type=0'
Tags=['动画短片','家庭','音乐','童年','浪漫','黑帮','女性']
if __name__=='__main__':
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')

    threads=[]
    
    t1=threading.Thread(target=source,args=(Q2,))
    threads.append(t1)

    t2=threading.Thread(target=isUkNew,args=(Q2,Q3,))
    threads.append(t2)
    
    t3=threading.Thread(target=searchHome,args=(Q3,Q4,))
    threads.append(t3)
    
    t4=threading.Thread(target=searchHome,args=(Q3,Q4,))
    threads.append(t4)
    
    t5=threading.Thread(target=searchHome,args=(Q3,Q4,))
    threads.append(t5)
    
    t6=threading.Thread(target=writeMySQL,args=(Q4,))
    threads.append(t6)
    
    t7=threading.Thread(target=queueSize,args=(Q1,Q2,Q3,Q4,))
    threads.append(t7)
    
    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()