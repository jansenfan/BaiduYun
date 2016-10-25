# -*- coding:utf-8 -*-
'''
Created on 2016��10��18��

@author: jansen_fan
'''
from Lib import getHtml
import urllib,urllib2,re,cookielib,time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import  MySQLdb as mdb
def WPS(url):  #返回搜索结果的url
    rawWord = raw_input("Enter your input: ")
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    
    startPage=0
    urlR=[]
    while(1):
        try:
            urlS=url+keyWord+'&start='+str(startPage)
            startPage=startPage+10
            print urlS
            html=getHtml(urlS)
            #print html
            reg=r'<a class="cse-search-result_content_item_top_a" href="(.+?)" rel="noreferrer"'
            regExp=re.compile(reg)
            items=re.findall(regExp,html)
            urlR=urlR+items
        except urllib2.HTTPError as err:
            if err.code==404:
                print "404：已搜索完毕"
                break
    return urlR

def isNull(url):
    try:
        response=urllib2.urlopen(i)
    except urllib2.HTTPError as err:
        if err.code==403:
            print "wait for a while"
    htmlT=response.read()
    reg=r'<title>(.+?)_'
    regExp=re.compile(reg)
    title=re.findall(regExp,htmlT)
    if title==[]:
        return 1
    else:
        return 0
def getHtmlByCookie(url):
    response=urllib2.urlopen(url)
    html=response.read()
    return html
#注意url中 amp; 问题
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
    driver.close()
    return res
def isBDYurl(url):#判断是否pan或者yun格式
    if (str(url).find('pan.baidu.com')!=-1) or (str(url).find('yun.baidu.com')!=-1):
        return 1
    else:
        return 0

def getUk(url):  #根据url，返回相应的uk：字符串格式
    reg=r'uk=(\d+)'
    regExp=re.compile(reg)
    uk=re.findall(regExp,url)
    return uk[0] 
def isUkNew(uk):
    pass

if __name__=='__main__':
    num=0
    cookie=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener=urllib2.build_opener(cookie)
    urllib2.install_opener(opener)
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    cur = con.cursor()
    con.select_db('baiduyun')
    '''
    cur.execute(sqlselect)
    tablerows=cur.fetchall()
    cur.execute('drop table if exists uklist')
    cur.execute('drop table if exists urllist')
    cur.execute('create table uklist(indez int not null  primary key auto_increment,uk varchar(20))') 
    cur.execute('create table urllist(indez int not null  primary key auto_increment,title varchar(100),url varchar(150),uk varchar(20))')
    '''
    '''
    #第一步：网盘搜结果呈现
    '''
    url=['http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q=']
    urlR=WPS(url[0])
    print urlR
    f=open('c:/PyProj/1.txt','w')
    for i in urlR:
        if isBDYurl(i):
            f.write(str(i))
            f.write('\n')
    f.close()
    
    '''
    #第二步：根据url中uk，搜索home，填充自己的数据库
    '''
    urlHome1='http://pan.baidu.com/share/home?uk='
    urlHome2='#category/type=0'
    for i in urlR:
        if isBDYurl(i):
            uk=getUk(i)
            print uk
            if cur.execute('select uk from uklist where uk=%s',uk)==0: #判断是否已经收录此uk
                cur.execute('insert into uklist(uk) values(%s)',uk)
                print '用户'+uk+':开始搜索'
                resList=[]
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
    
    con.commit()
    cur.close()
    con.close()
    print '本次搜索结果搜录完毕\n共收录'+str(num)+'个链接'
                
    
    