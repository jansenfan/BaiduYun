# -*- coding:utf-8 -*-
'''
Created on 2016��10��18��

@author: jansen_fan
'''
from threading import Thread
from Lib import getHtml
import urllib,urllib2,re,cookielib,time,random,ThreadPool
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import  MySQLdb as mdb
from Queue import Queue
q1=Queue()#[url,pw]
q2=Queue()#uk
q3=Queue()#uk
q4=Queue()#[title,url,uk]
poolsize=5
pool = ThreadPool(poolsize) 
requests = ThreadPool.makeRequests(handlePw(), q1, isUkNew()) 
[pool.putRequest(req) for req in requests] 
pool.wait()
source=[['http://pan.baidu.com/s/1nuOQgSp','oyds'],['http://pan.baidu.com/s/1qW7Eu8O','97k2'],['http://pan.baidu.com/s/1dFhxudr','6cd7'],['http://pan.baidu.com/s/1jIuddNw','snt3'],['http://pan.baidu.com/s/1kV8UiHp','pvgt']]

def handlePw():
    while True:
        item=q1.get()
        url=item[0]
        pd=item[1]
        driver = webdriver.PhantomJS(executable_path='C:/PyProj/DRIVER/phantomjs/bin/phantomjs')
        driver.get(url)
        time.sleep(2)
        print url
        print pd
        if pd!='null':
            driver.get(url)
            tempUrl=driver.current_url
            #print '识别地址:'+tempUrl
            startUkPos=tempUrl.find('uk=')
            #print startUkPos
            if startUkPos==-1:  # no page exist
                uk='null'
            else:
                uk=tempUrl[startUkPos+3:]  #string 变量
            driver.quit()
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
        print uk
        q2.put(uk)
        q1.task_done()

def isUkNew():
    pass

for i in range(2):
    t=Thread(target=handlePw)
    t.daemon=True
    t.start()


for i in source:
    q1.put(i)

q1.join()
