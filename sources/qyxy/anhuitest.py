#!/usr/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import os,os.path
from bs4 import BeautifulSoup

class Anhui(object):
	def __init__(self):
		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	def crack_checkcode(self):
		resp = self.reqst.get('http://www.ahcredit.gov.cn/search.jspx')
		if resp.status_code != 200:
			return None
		resp = self.reqst.get('http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.5074288535327053')
		if resp.status_code != 200:
			return None
		with open('s.jpg', 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('qinghai')
		ck_code = code_cracker.predict_result('s.jpg')
		return ck_code

	def crawl_check_page(self):
		count = 0
		while count < 3:
			ckcode = self.crack_checkcode()[1]
			print ckcode
			data = {'name':'340000000002071','verifyCode':ckcode}
			resp = self.reqst.post('http://www.ahcredit.gov.cn/search.jspx',data=data)
			if resp.status_code != 200:
				print 'error...(crawl_check_page)'
				continue
			if resp.content.find('true')>=0:
				temp={'checkNo':ckcode,'entName':'340000000002071'}
				resp = self.reqst.post('http://www.ahcredit.gov.cn/searchList.jspx',data=temp)
				if resp.status_code != 200:
					print 'error...post'
					count += 1
					continue
				soup = BeautifulSoup(resp.content,'html5lib')
				divs = soup.find(class_='list')
				if divs == None:continue
				print divs.ul.li.a['href']
				resp = self.reqst.get('http://www.ahcredit.gov.cn'+ divs.ul.li.a['href'])
				print divs.ul.li.a['href'][divs.ul.li.a['href'].find('id=')+3:]
				if resp.status_code == 200:
					soup = BeautifulSoup(resp.content,'html5lib')
					table1 = soup.find(class_='detailsList')
					f = open('table1.txt', 'w')
					for index, tr in enumerate(table1.find_all('tr')):
						if index==0:continue
						for th,td in zip(tr.find_all('th'),tr.find_all('td')):
							print >> f,th.get_text().strip(),td.get_text().strip()
					f.close()
					f = open('table2.txt', 'w')
					table2 = soup.find('table',attrs={'cellspacing':"0","cellpadding":"0",'class':"detailsList",'id':"touziren"})
					print type(table2)
					table2 = table2.find_all('th',attrs={'width':"20%",'style':"text-align:center;"})
					for item in table2:
						print >>f,item.get_text()
					preitem = None
					for i in range(1,10):
						resp = self.reqst.get('http://www.ahcredit.gov.cn/QueryInvList.jspx?pno=' + str(i) +'&mainId=4EF6A3BF5498AAA4AEEEB80A05878626')
						if preitem == resp.content:
							print i
							break
						preitem = resp.content
						soup = BeautifulSoup(resp.content,'html5lib')
						table2 = soup.find_all('td')
						for item in table2:
							if item.a:
								urlid = item.a['onclick'][item.a['onclick'].find('window.open')+13:-2]
								print 'http://www.ahcredit.gov.cn'+urlid
								print item.get_text().strip()
								resp = self.reqst.get('http://www.ahcredit.gov.cn'+urlid)
								tempsoup = BeautifulSoup(resp.content,'html5lib')
								tabeldetail = tempsoup.find('table',attrs={'cellpadding':"0" ,'cellspacing':"0", 'class':"detailsList" })
								ths = tabeldetail.find_all('th')
								tds = tabeldetail.find_all('tr')
								for th in ths:
									print th.get_text().strip()
								for td in tds:
									print td.get_text().strip()
							else :
								print item.get_text().strip()
						return True
					else :
						print 'error...if'
						count += 1
						continue
			return False

anhui = Anhui()
anhui.crawl_check_page()