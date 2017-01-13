# -*- coding:utf-8 -*-
import urllib2,re,cookielib,httplib,socket,urllib,random,time
from bs4 import BeautifulSoup
header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'  }  
timeOut=50
def getHtml(url):
    request=urllib2.Request(url,headers=header)
    urllib2.Request
    try:
        html=urllib2.urlopen(request,timeout=timeOut).read()
    except httplib.IncompleteRead, e:
        html = e.partial
    except socket.timeout as e:
        html=str(e)
    return html

def isPageNull(url):
    try:
        response=urllib2.urlopen(url)
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
    cookie=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener=urllib2.build_opener(cookie)
    urllib2.install_opener(opener)
    response=urllib2.urlopen(url)
    html=response.read()
    return html


def Bing(rawWord):
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    url1='http://cn.bing.com/search?q='
    url2='+site%3apan.baidu.com&first=' #followed by item number
    
    
    resList=[]
    reg1=r'<h2>(.*?)</h2>'
    reg2=r'href="(.*?)" h=.*?>(.*?)</a>'
    regExp1=re.compile(reg1)
    regExp2=re.compile(reg2)
    breakFlag='class="sb_pagN"'
    
    itemNum=1
    while True:
        url=url1+keyWord+url2+str(itemNum)
        html=getHtml(url)
        items=re.findall(regExp1,html)
        for i in items:
            item=re.findall(regExp2,i)
            if item!=[]:
                res=list(item[0])
                res[0]=res[0].replace('amp;','')
                res[1]=res[1].replace('<strong>','')
                res[1]=res[1].replace('</strong>','')
                res[1]=res[1].replace('...','')
                tagPos=res[1].find('_免费高速')
                res[1]=res[1][:tagPos]
                resList.append(res)
        if (html.find(breakFlag)==-1):
            break
        itemNum+=10
        time.sleep(random.randint(2,10))
    return resList


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

def isAlive(ip,port):
        proxy={'http':"http://"+ip+':'+port}
        print proxy
        header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'  }  
        proxy_support=urllib2.ProxyHandler(proxy)
        opener=urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        test_url="http://www.qq.com"
        req=urllib2.Request(test_url,headers=header)
        try:
            resp=urllib2.urlopen(req,timeout=10)
            if resp.code==200:
                print "work"
                return True
            else:
                print "not work"
                return False
        except :
            print "Not work"
            return False
    
def S_Tebaidu(rawWord):
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    
    ukList=[]
    pageNum=0
    
    url1='http://www.tebaidu.com/search.asp?r=0&wd='
    url2='&p=&page=' #followed by page number
    url=url1+keyWord
    reg=r'user-(.*?)-1'
    regExp=re.compile(reg)
    html=getHtml(url)
    tempList=re.findall(regExp,html)
    ukList=ukList+tempList
    while(html.find("下一页")!=-1):
        pageNum=pageNum+1
        url=url1+keyWord+url2+str(pageNum)
        html=getHtml(url)
        tempList=re.findall(regExp,html)
        ukList=ukList+tempList
    setList=set(ukList)
    resList=list(setList)
    return resList

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
    html=getHtml(url)
    tempList=re.findall(regExp,html)
    ukList=ukList+tempList
    while(html.find("下一页")!=-1):
        pageNum=pageNum+1
        url=url1+keyWord+url2+str(pageNum)
        html=getHtml(url)
        tempList=re.findall(regExp,html)
        ukList=ukList+tempList
    setList=set(ukList)
    resList=list(setList)
    return resList