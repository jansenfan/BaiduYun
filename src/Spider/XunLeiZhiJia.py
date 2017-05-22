# -*- coding:utf-8 -*-
from Lib import getHtml
import re 
import MySQLdb as mdb
IvdList=[22975]
import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')
logger=logging.getLogger(__name__)

def updateList():
    url='http://www.xl720.com/'
    f=open('C:/PyProj/GitHub/BaiduYun/src/Spider/hotList.txt','w')
    html=getHtml(url)
    items=re.findall(r'topthree(.*?)</a>',html,re.S)
    for i in items:
        titleTemp=i[i.find('blank')+7:]
        if titleTemp.find(' ')!=-1:
            title=titleTemp.split(' ')[0]
        if title.find('：')!=-1:
            title=title.split('：')[0]
        f.write(title)
        f.write('\n')
    f.close()

def xl720(page):
    url1='http://www.xl720.com/thunder/'
    #pageNum=16073
    url2='.html'
    pageNum=page
    while True:
        pageNum+=1
        if pageNum<page+100 and (pageNum not in IvdList):
            url=url1+str(pageNum)+url2
            logger.debug(url)
            html=getHtml(url)
            if html.find('download-link')!=-1:
                res=re.findall(r'<div class="download-link"><i></i><a href="(.*?)" rel=.*?>(.*?)</a>',html,re.S)
                title=res[0][1]
                link=res[0][0]
                logger.debug('第'+str(pageNum)+'页：'+title)
                cur=con.cursor()
                if len(title)<99:
                    cur.execute('insert into books.books_xunlei(title,link,pageNum) values(%s,%s,%s)',[title,link,pageNum])
                con.commit()
                cur.close()
        else:
            logger.info('Daily Update Completed!!')
            break
                                
if __name__=='__main__':
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('books')
    cur=con.cursor()
    cur.execute('select pageNum from books.books_xunlei order by id desc limit 1')
    updateList()
    key=cur.fetchone()
    page=key[0]
    cur.close()
    #print '开始页数：'+str(page)
    logger.info('Start Page Number: '+str(page))
    xl720(int(page))    
    con.close()