import urllib2,re,cookielib,httplib

header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'  }  
def getHtml(url):
    request=urllib2.Request(url,headers=header)
    urllib2.Request
    try:
        html = urllib2.urlopen(request).read()
    except httplib.IncompleteRead, e:
        html = e.partial
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
