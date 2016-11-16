# -*- coding:utf-8 -*-
'''
Created on 2016��11��5��

@author: jansen_fa
'''


import threading,random,time,urllib,urllib2,re
import MySQLdb as mdb

from Queue import Queue
from random import sample
from bs4 import BeautifulSoup
from Lib import getHtml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
def WPS(rawWord):  #return uk and password  【[url,uk],[url,uk]...,[url,uk]】
    #rawWord = raw_input("Enter your input: ")
    url='http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q='
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    
    startPage=0
    urlR=[]
    while(1):
        try:
            urlS=url+keyWord+'&start='+str(startPage)
            startPage=startPage+10
            #print urlS
            print '网盘搜结果检索第'+str(startPage/10)+'页'
            html=getHtml(urlS)
            while html.find('timed out')!=-1:
                print 'timeout'
                return urlR
            #print html
            soup=BeautifulSoup(html,'lxml')
            tempResult=soup.find_all('td',class_="cse-search-result_content_item_table_td")
            #print tempResult
            for i in tempResult:
                startUrlPos=str(i).find('href')+6
                endUrlPos=str(i).find('onclick')-2
                urltemp=str(i)[startUrlPos:endUrlPos]
                startCodePos=str(i).find('提取密码')
                if startCodePos==-1:
                    res=[urltemp,'null']
                else:
                    code=str(i)[startCodePos+16:startCodePos+20]
                    res=[urltemp,code]
                urlR.append(res)
                #print res
                #print urlR
                    
        except urllib2.HTTPError as err:
            if err.code==404:
                print "已搜索完毕"
                break
    return urlR

if __name__=='__main__':
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    startID=144
    cur=con.cursor()
    while True:
        cur.execute('select title from titlelist where id=%s',startID)
        item=cur.fetchone()
        title=item[0]
        print title
        print '当前读取第'+str(startID)+'条记录'
        startID+=1
        if not(title):# noneType or not
            break
        urlR=WPS(title)
        print urlR
        for i in urlR:
            if len(i[0])<=150:
                i[0]=i[0].replace('amp;','')
                cur.execute('insert into checklist(url,password) values(%s,%s)', i)
        con.commit()
        time.sleep(random.randint(100,150))
        
    cur.close()
    con.close()
        