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
                cur.execute('insert into baiduyun.taglist(title,url,uk) values(%s,%s,%s)',[item[0],url,item[2]])
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


def checkThread(iniNameList):
    while True:
        time.sleep(10)
        nowNameList=[]
        now=threading.enumerate()
        #print 'now :'
        #print now
        for i in now:
            nowNameList.append(i.getName())
            
        for j in iniNameList:
            if j in nowNameList:
                pass
            else:
                print "threading "+j+" stopped, now restart"
                if j in ['t1','t2','t3']:
                    t=threading.Thread(target=searchHome,args=(Q3,Q4,))
                if j=='t4':
                    t=threading.Thread(target=writeMySQL,args=(Q4,))
                if j=='t5':
                    t=threading.Thread(target=queueSize,args=(Q1,Q2,Q3,Q4,))
                t.setName(j)
                t.start()
        time.sleep(300)



Q1=Queue()
Q2=Queue()
Q3=Queue()
Q4=Queue()
urlHome1='http://pan.baidu.com/share/home?uk='
urlHome2='#category/type=0'
if __name__=='__main__':
    
    #startNum=178713
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    cur=con.cursor()
    #update books.searchresult
    cur.execute('select url from books.books_searchresult order by num desc limit 1')
    res=cur.fetchone()
    cur.execute('select id from baiduyun.taglist where url=%s',[str(res[0])])
    num=cur.fetchone()[0]
    cur.execute('insert into books.books_searchresult(title,url) select title,url from baiduyun.taglist where id>%s',[num])
    
    con.commit()

    # get start number
    cur.execute('select uk from baiduyun.taglist order by id desc limit 1000')
    res=cur.fetchall()
    res=list(set(res))
    temp=[]
    for i in res:
        #temp.append(str(i[0]))
        cur.execute('select indez from baiduyun.uklist where uk=%s',[str(i[0])])
        indez=cur.fetchone()[0]
        temp.append(indez)

    startNum=max(temp)+1
    
    cur.execute('select * from baiduyun.uklist where indez>=%s',startNum)
    items=cur.fetchall()
    cur.close()
    
    for i in items:
        Q3.put(str(i[1]))

    threads=[]
    iniNameList=['t1','t2','t3','t4','t5','t6']
    t1=threading.Thread(target=searchHome,args=(Q3,Q4,))
    t1.setName('t1')
    threads.append(t1)
    
    t2=threading.Thread(target=searchHome,args=(Q3,Q4,))
    t2.setName('t2')
    threads.append(t2)
    
    t3=threading.Thread(target=searchHome,args=(Q3,Q4,))
    t3.setName('t3')
    threads.append(t3)
    
    t4=threading.Thread(target=writeMySQL,args=(Q4,))
    t4.setName('t4')
    threads.append(t4)
    
    t5=threading.Thread(target=queueSize,args=(Q1,Q2,Q3,Q4,))
    t5.setName('t5')
    threads.append(t5)
    
    t6=threading.Thread(target=checkThread,args=(iniNameList,))
    t6.setName('t6')
    threads.append(t6)
    
    for t in threads:
        t.setDaemon(True)
        t.start()
        
    for t in threads:
        t.join()
        
    con.commit()
    con.close()