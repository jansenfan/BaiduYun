# -*- coding:utf-8 -*-
'''
Created on 2016��10��18��

@author: jansen_fan
'''
from threading import Thread
from Lib import getHtml
import urllib,urllib2,re,cookielib,time,random,threadpool
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
    


def handlePw(url,pd):#input: password & url; return: uk[string]
    driver = webdriver.PhantomJS(executable_path='C:/PyProj/DRIVER/phantomjs/bin/phantomjs')
    driver.get(url)
    time.sleep(2)
    #print url 
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
    
    
    
    
def searchHome(url):#根据home的url，返回所有子项url和name
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
    return res

     

    
i=q.get()    
if isBDYurl(i[0]):
    i[0]=i[0].replace('amp;','')
    uk=getUk(i[0])
    print '初始地址:'+i[0]
    print '初始密码:'+i[1]
    if uk=='null':
        uk=handlePw(i[0],i[1])
    print '用户编号:'+uk
    if uk!='null':
        if cur.execute('select uk from uklist where uk=%s',uk)==0: #判断是否已经收录此uk
            cur.execute('insert into uklist(uk) values(%s)',uk)
            print '用户'+uk+':开始搜索'
            resList=[]
            urlHome1='http://pan.baidu.com/share/home?uk='
            urlHome2='#category/type=0'
            urlHome=urlHome1+uk+urlHome2
            try:
                resList=searchHome(urlHome)
            except urllib2.HTTPError as err:
                print err
            for j in resList:
                num=num+1
                cur.execute('insert into urllist(title,url,uk) values(%s,%s,%s)',[j[0],j[1],uk])
            print '用户'+uk+':搜索完毕'
            print '当前收录量：'+str(num)
        else:
            print 'uk已收录，跳过'