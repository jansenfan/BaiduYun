import urllib2
header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'  }  
def getHtml(url):
    request=urllib2.Request(url,headers=header)
    urllib2.Request
    response=urllib2.urlopen(request)
    html=response.read()
    return html