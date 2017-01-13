# -*- coding:utf-8 -*-
'''
Created on 2017��1��9��

@author: jansen_fan
'''
import MySQLdb as mdb
if __name__=='__main__':
    con = mdb.connect(host = 'localhost',user = 'root',passwd = '123456',charset="utf8")
    con.select_db('baiduyun')
    cur = con.cursor()
    startNum=330747  
    processNum=0
    paceNum=10000
    #cur.execute('CREATE TABLE newUrl(id int NOT NULL AUTO_INCREMENT PRIMARY key,title varchar(100),url varchar(50),uk varchar(20))')
    while True:
        cur.execute('select * from urllist where indez>=%s and indez<%s',[startNum,(startNum+paceNum)])
        startNum=startNum+paceNum
        items=cur.fetchall()
        if items==():
            break
        for i in items:
            processNum=processNum+1
            print processNum
            title=str(i[1])
            url=str(i[2])
            if(url.find('uk=')!=-1):
                continue
            url=url[23:]
            uk=str(i[3])
            #if cur.execute('select url from newUrl where url=%s',url)==0: #判断是否已经收录此url
            cur.execute('insert into newUrl(title,url,uk) values(%s,%s,%s)',[title,url,uk])
        
        con.commit()
    cur.close()
    con.close()
            
