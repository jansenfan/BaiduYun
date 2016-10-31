import urllib2
import httplib
header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'  }  
def getHtml(url):
    request=urllib2.Request(url,headers=header)
    urllib2.Request
    try:
        html = urllib2.urlopen(request).read()
    except httplib.IncompleteRead, e:
        html = e.partial
    return html