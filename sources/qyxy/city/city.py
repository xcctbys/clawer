#-*- coding:UTF-8 -*-

import requests
import bs4
import re
import logging
import Queue
import multiprocessing
import  sys
import urllib
from bs4 import BeautifulSoup


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



class  Spider(object):
	
    def __init__(self, keywords_path):
        self.keywords_path = keywords_path
        self.query_url = "http://report.bbdservice.com/show/searchCompany.do"
        self.output_path = "enterprise.out"
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        }
        self.keywords = []
        self.result = [] #{'name':'', 'no':'', 'where':''}
        
    def transform(self):
        self._load_keywords()
        for keyword in self.keywords:
            self._parse(keyword)
            
        with open(self.output_path, "w") as f:
            for item in self.result:
                f.write((u"%s,%s,%s" % (item["name"], item["no"], item["where"])).encode("utf-8"))
        
    def _load_keywords(self):
        with open(self.keywords_path) as f:
            for line in f:
                self.keywords.append(line.strip())
                
    def _parse(self, keyword):
        url = "%s?%s" % (self.query_url, urllib.urlencode({"term": keyword}))
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            logging.warn("request %s, return code %d", url, r.status_code)
            return
        
        data = {"name":"", "no":"", "where":""}
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"class":"search-r fl p20 pl40 w60p"})
        ul = div.find("ul")
        lis = ul.find_all("li")
        for li in lis:
            h4 = li.find("h4")
            if not h4:
                continue
            title = h4.get_text().strip().strip("\"")
            if title != keyword:
                continue
            data["name"] = title
            p = li.find("p", {"class":"colorText4 f12"})
            content = p.get_text().strip()
            tmp = content.split(" ")
            print tmp
            
        self.result.append(data)
        
	def load(self):
		with open (self.path,'r') as f:
			for line in f.readlines():
				self.kw=line.split(',')[1].strip()
				self.city=line.split(',')[0].strip()
				print self.kw
				print self.city
				url='http://report.bbdservice.com/show/searchCompany.do?term='+self.kw
				headers={
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
	            }
				self.url=url.decode('utf8')
				b=spynner.Browser()
				b.create_webview()
				b.load(self.url,headers)
				html=b.html.encode('utf8')
				soup=bs4.BeautifulSoup(html)
				q.put(soup)

	def parse(self):
		while True:
			try:

				self.soup=q.get()

				self.text=self.soup.find_all('p',class_='colorText4 f12')
				for s in self.text:
					s=str(s.text)
					if self.kw in s:
						r=re.compile("注册号：([\\s\\S]*?) 类型")
						self.number=r.findall(s)[0]
						open('city2.txt','a').write(self.kw+','+self.city+','+self.number+'\n')
						print 'successful...'
						break
			except q.empty:
				break
		print 'complete...'


if __name__ == "__main__":
    spider = Spider("company_bonds.txt")
    spider.transform()

