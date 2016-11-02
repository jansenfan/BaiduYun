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
import random
import threading
def WPS(rawWord):  #return uk and password  【[url,uk],[url,uk]...,[url,uk]】
    #rawWord = raw_input("Enter your input: ")
    Dict={'a':rawWord}
    temp=urllib.urlencode(Dict)
    keyWord=temp[2:]
    urlIni='http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q='
    startPage=0
    urlR=[]
    while(1):
        try:
            urlS=urlIni+keyWord+'&start='+str(startPage)
            startPage=startPage+10
            print urlS
            print '网盘搜结果检索第'+str(startPage/10)+'页'
            html=getHtml(urlS)
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

def isBDYurl(url):#判断是否pan或者yun格式
    if (str(url).find('pan.baidu.com')!=-1) or (str(url).find('yun.baidu.com')!=-1):
        return 1
    else:
        return 0

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
    
def getUk(url):  #根据url，返回相应的uk：字符串格式
    reg=r'uk=(\d+)'
    regExp=re.compile(reg)
    uk=re.findall(regExp,url)
    if len(uk):
        return uk[0]
    else:
        return 'null'
     
def keyWordLib(): #return hot keyword[list]
    hotUrl=['http://www.bdybbs.com/top/','http://top.baidu.com/category?c=10','http://xiazai.zol.com.cn/download_order/soft_order.html']
    reg=[r'target="_blank">(.+?)</a></li>',r'<a target="_blank" title="(.+?)"','target="_blank" class="title" title="(.+?)"']
    charsetUrl=['utf8','gb2312','gbk']
    hotList=[]
    for i in range(len(hotUrl)):
        html=getHtml(hotUrl[i])
        regTemp=reg[i]
        regExp=re.compile(regTemp)
        items=re.findall(regExp,html)
        newItems=[]
        if charsetUrl[i]!='utf8':
            for item in items:
                newItems=newItems+[item.decode(charsetUrl[i]).encode('utf8')]
        else:
            newItems=items
        hotList=hotList+newItems
    return hotList

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

if __name__=='__main__':
    cookie=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener=urllib2.build_opener(cookie)
    urllib2.install_opener(opener)
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    cur = con.cursor()
    #cur.execute('CREATE TABLE uklist(id int NOT NULL AUTO_INCREMENT PRIMARY key,uk varchar(20))')
    #cur.execute('CREATE TABLE urllist(id int NOT NULL AUTO_INCREMENT PRIMARY key,title varchar(100),url varchar(150),uk varchar(20))')
    #Tags=['爱情','喜剧','动画','剧情','科幻','动作','经典','悬疑','青春','犯罪','惊悚','文艺','搞笑','纪录片','励志','恐怖','战争','短片','魔幻','黑色幽默','传记','情色','感人','暴力','动画短片','家庭','音乐','童年','浪漫','黑帮','女性' '同志','史诗','童话','烂片','cult']
    Tags=['搞笑','纪录片','励志','恐怖','战争','短片','魔幻','黑色幽默','传记','情色','感人','暴力','动画短片','家庭','音乐','童年','浪漫','黑帮','女性' '同志','史诗','童话','烂片']
    #url=['http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q=']
    urlHome1='http://pan.baidu.com/share/home?uk='
    urlHome2='#category/type=0'

    
    for tag in Tags:
        doubanList=doubanMovieList(tag)
        for item in doubanList:
            print '当前关键词：'+item
            urlR=WPS(item)
            num=0
            for i in urlR:
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
                print '本次搜索结果搜录完毕\n共收录'+str(num)+'个链接'
            
    cur.close()
    con.close()