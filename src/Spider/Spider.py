# -*- coding:utf-8 -*-
'''
Created on 2016��10��18��

@author: jansen_fan
'''
from Lib import getHtml
import urllib,urllib2,re,cookielib
from selenium import webdriver
from bs4 import BeautifulSoup
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
                print "已搜索完毕"
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
    html=driver.page_source
    soup=BeautifulSoup(html,'lxml')
    tempResult=soup.find_all('a',class_="file-handler")
    for i in tempResult:
        startUrlPos=str(i).find('http:')
        endUrlPos=str(i).find('style=')
        url=str(i)[startUrlPos:endUrlPos-2]
        url.replace('amp;','')
        startNamePos=str(i).find('title')+7#加7删除'title='的影响
        endNamePos=str(i).find('unselectable')-2
        name=str(i)[startNamePos:endNamePos]
        res.append([name,url])
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

if __name__=='__main__':
    
    cookie=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener=urllib2.build_opener(cookie)
    urllib2.install_opener(opener)
    '''
    #第一步：网盘搜结果呈现
    '''
    url=['http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q=']
    urlR=WPS(url[0])
    print urlR
    f=open('f:/PyProj/1.txt','w')
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
    fUk=open('f:/PyProj/ukList.txt','a')
    for i in urlR:
        if isBDYurl(i):
            uk=getUk(i)
            print '用户'+uk+':开始搜索'
            fUk.write(uk)
            fUk.write('\n')
            resList=[]
            urlHome=urlHome1+uk+urlHome2
            try:
                resList=searchHome(urlHome)
            except urllib2.HTTPError as err:
                print err
            f=open('f:/PyProj/'+uk+'.txt','w')
            for j in resList:
                f.write(j[0])
                f.write('\n')
                f.write(j[1])
                f.write('\n')
            f.close()
            print '用户'+uk+':搜索完毕'
    fUk.close()
    print '全部搜索完毕'
                
    
    