#coding=utf-8

import urllib
import string, urllib2
import re   
from bs4 import BeautifulSoup

#定义搜索函数  
def sina_search(url,keyword_name,media_name):

#------------ 抽取文章链接以及文章发布时间 ---------------------
    url = urllib.quote(url,':?=/&+%')
#    print url
    sName = '1_1url.txt' #生成文件的文件名  
#    print u'正在抽取网页内文章链接，并将其存储为' + sName + '......'  
    f = open(sName,'w+')
    page = urllib2.urlopen(url + '&col=&source=&from=&country=&size=&time=&a=&page=1&pf=2131425492&ps=2132080888&dpc=1')
    soup = BeautifulSoup(page,"html5lib")
    num = str(soup.find('div',{'class','l_v2'}).contents).decode("unicode_escape").replace(',','')
    news_num = int(re.findall(r'\d+',num)[0])
    print u'一共获取到' + str(news_num) + u'条url，准备抽取中......'
    j = 1
    for i in range(1, ((news_num-1)/10)+2):
        page = urllib2.urlopen(url + '&col=&source=&from=&country=&size=&time=&a=&page=' + str(i)+'&pf=2131425492&ps=2132080888&dpc=1')
        
        try:        #跳过请求错误
            page = urllib2.urlopen(url + '&col=&source=&from=&country=&size=&time=&a=&page=' + str(i)+'&pf=2131425492&ps=2132080888&dpc=1')
        except:     #发生错误继续执行循环
            continue
        
        soup = BeautifulSoup(page,"html5lib")
        all_h = soup.find_all("h2")
        for h in all_h:
            news_a = h.find('a')
            news_link = news_a['href']
#            print news_link
#            f.write(news_link,)
#            f.write('\n')
            if 'http://finance.sina.com' in news_link:      #链接格式判断
                print u'正在抽取网页内第' + str(j) + u'文章链接，并将其存入' + sName + '......'
                f.write(news_link,)
                f.write('\n')
                j+=1
            else:
                continue
    f.close()
    
    
#----------------------------------------------------------- 


#----------- 用户输入关键字以及媒体源实现查询功能 ----------------  
keyword_name = str(raw_input('Please enter key word:\n'))  
media_name = str(raw_input('Please enter search media:\n'))
sinaurl = 'http://search.sina.com.cn/?c=news&q=' + keyword_name + '+O%3A' + media_name + '&range=all&num=10'

#----------------------------------------------------------  
   
  
#调用
sina_search(sinaurl,keyword_name,media_name)