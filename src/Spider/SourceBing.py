# -*- coding:utf-8 -*-
'''
Created on 2016��11��15��

@author: jansen_fan
'''
import urllib,re,time,random
from Lib import getHtml
def SourceBing(rawWord):
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
                tagPos=res[1].find('_免费高速下载|')
                res[1]=res[1][:tagPos]
                resList.append(res)
        if (html.find(breakFlag)==-1):
            break
        itemNum+=10
        time.sleep(random.randint(2,10))
    return resList

if __name__=='__main__':
    i='纳尼亚传奇'
    reslist=SourceBing(i)
    print reslist
    for i in reslist:
        print i[0]
        print i[1]
        