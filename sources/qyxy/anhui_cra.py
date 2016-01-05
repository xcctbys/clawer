#!/usr/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import os,os.path
from bs4 import BeautifulSoup

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
	import settings_pro as settings
else:
	import settings

class AnhuiCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/anhui/'
	#验证码图片的存储路径
    	ckcode_image_path = settings.json_restore_path + '/anhui/ckcode.jpg'

	def __init__(self):
		self.id = None
		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://www.ahcredit.gov.cn/search.jspx',
				'searchList':'http://www.ahcredit.gov.cn/searchList.jspx',
				'validateCode':'http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.5074288535327053',
				'QueryInvList':'http://www.ahcredit.gov.cn/QueryInvList.jspx?'}

		self.mysearchdict = {'businessPublicity':'http://www.ahcredit.gov.cn/businessPublicity.jspx?',
				'enterprisePublicity':'http://www.ahcredit.gov.cn/enterprisePublicity.jspx?',
				'otherDepartment':'http://www.ahcredit.gov.cn/otherDepartment.jspx?',
				'justiceAssistance':'http://www.ahcredit.gov.cn/justiceAssistance.jspx?'}
		self.jsp_one_dict = {u'基本信息':None, u'变更信息':'/QueryAltList.jspx?',u'主要人员信息':'/QueryMemList.jspx?', \
				u'分支机构信息':'/QueryChildList.jspx?',u'清算信息':None,u'动产抵押登记信息':None,\
				u'股权出质登记信息':None,u'行政处罚信息':None,u'经营异常信息':None,\
				u'严重违法信息':None,u'抽查检查信息':None,u'股东（发起人）信息':'/QueryInvList.jspx?'}
	def get_check_num(self):
		resp = self.reqst.get(self.mydict['search'])
		if resp.status_code != 200:
			return None
		resp = self.reqst.get(self.mydict['validateCode'])
		if resp.status_code != 200:
			return None
		with open('s.jpg', 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('qinghai')
		ck_code = code_cracker.predict_result('s.jpg')
		return ck_code[1]

	def get_id_num(self, findCode):
		count = 0
		while count < 3:
			check_num = self.get_check_num()
			print check_num
			data = {'name':findCode,'verifyCode':check_num}
			resp = self.reqst.post(self.mydict['search'],data=data)
			if resp.status_code != 200:
				print 'error...(get_id_num)'
				continue
			if resp.content.find('true')>=0:
				temp={'checkNo':check_num,'entName':findCode}
				resp = self.reqst.post(self.mydict['searchList'],data=temp)
				if resp.status_code != 200:
					print 'error...post'
					count += 1
					continue
				soup = BeautifulSoup(resp.content,'html5lib')
				divs = soup.find(class_='list')
				if divs == None:continue
				mainId = divs.ul.li.a['href'][divs.ul.li.a['href'].find('id=')+3:]
				break
		return mainId

	def get_tables(self, url):
		resp = self.reqst.get(url)
		if resp.status_code == 200:
			tables = BeautifulSoup(resp.content, 'html5lib').find_all('table')
			return [table for table in tables if (table.find_all('th') or table.find_all('a')) ]

	def test_print_table(self, tables):
		for table in tables:
			print table

	def do_with_specially(self, table_specially):
		return None

	def do_with_hasnext(self, head, table_head, table_next):
		print 'do_with_hasnext',head
		if head == u'股东（发起人）信息':
			ths = table_head.find_all('th')[1:]
			print [th.get_text() for th in ths]
			a_count = len(table_next.find_all('a'))
			print a_count
			for i in range(1, a_count+1):
				tempresp = self.reqst.get(self.mydict['QueryInvList']+'pno='+str(i)+'&mainId='+self.id)
				if tempresp.status_code == 200:
					tempsoup = BeautifulSoup(tempresp.content)
					for tr in tempsoup.find_all('tr'):
						#print [td.get_text().strip() if td.get_text()  else None for td in tr.find_all('td')]
						details = []
						for td in tr.find_all('td'):
							if td.find('a'):
								temp = self.reqst.get( self.mydict['eareName'] + td.a['onclick'][13:-2])
								if temp.status_code == 200:
									detail_soup = BeautifulSoup(temp.content)
									specially_dict = self.do_with_specially(detail_soup)
								else:
									print 'error...temp'
							else:

								details.append(td.get_text().strip() if td.get_text() else None)
						print len(details), details, specially_dict
				else :
					print 'error...tempurl'
		elif head == u'企业年报':
			pass
		else:
			ths = table_head.find_all('th')[1:]
			print [th.get_text() for th in ths]
			a_count = len(table_next.find('a'))
			print a_count
			for i in range(1, a_count+1):
				tempresp = self.reqst.get(self.mydict['eareName'] + self.jsp_one_dict[head] + 'pno='+str(i) + '&mainId='+self.id)
				if tempresp.status_code == 200:
					tempsoup = BeautifulSoup(tempresp.content)
					for tr in tempsoup.find_all('tr'):
						print [td.get_text().strip() if td.get_text() else None for td in tr.find_all('td')]




	def do_with_nonext(self, head, table_head, table_content):
		print 'do_with_nonext', head
		tds = table_head.find_all('td')
		ths = table_head.find_all('th')[1:]
		print len(tds), len(ths)
		if len(tds)>0:
			print [th.get_text().strip() for th in ths]
			print [td.get_text().strip()  if td.get_text() else None for td in tds]
		else:
			print [th.get_text().strip() for th in ths]
			content_tds = table_content.find_all('td')
			if len(content_tds) == 0:
				print [None for th in ths]
			else:
				print [td.get_text().strip() if td.get_text() else None for td in table_content.find_all('td')]

	def get_json_one(self, tables):
		count_table = len(tables)
		for i,table in enumerate(tables):
			try:
				if table.tr.th.get_text().split('\n')[0].strip() in [u'基本信息', u'变更信息',u'主要人员信息',u'分支机构信息',\
									u'清算信息',u'动产抵押登记信息',u'股权出质登记信息',u'行政处罚信息',\
									u'经营异常信息',u'严重违法信息',u'抽查检查信息',u'股东（发起人）信息' ]:
					if i !=0 and i+2 < count_table and len(tables[i+2].find_all('a'))>1:
						print i,'have next',
						# print tables[i]
						# print tables[i+2]
						self.do_with_hasnext(table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+2])
					elif  i+1<count_table:
						print i,'no next'
						self.do_with_nonext(table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+1])

			except AttributeError:
				pass
	def get_json_two(self, tables):
		pass
	def get_json_three(self, tables):
		pass
	def get_json_four(self, tables):
		pass

	def run(self, findCode):
		self.id = self.get_id_num(findCode)
		tableone = self.get_tables(self.mysearchdict['businessPublicity'] + 'id=' +self.id)
		self.get_json_one(tableone)
		tabletwo = self.get_tables(self.mysearchdict['enterprisePublicity'] + 'id=' +self.id)
		self.get_json_two(tabletwo)
		tablethree = self.get_tables(self.mysearchdict['otherDepartment'] + 'id=' +self.id)
		self.get_json_three(tablethree)
		tablefour = self.get_tables(self.mysearchdict['justiceAssistance'] + 'id=' +self.id)
		self.get_json_four(tablefour)


anhui = AnhuiCrawler()
anhui.run('340000000002071')
anhui.run('340000000006066')