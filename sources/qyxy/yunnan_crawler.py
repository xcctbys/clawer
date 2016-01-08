#!/usr/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import os,os.path
from crawler import CrawlerUtils
from bs4 import BeautifulSoup

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
	import settings_pro as settings
else:
	import settings

class YunnanCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/yunnan/'
	#验证码图片的存储路径
    	ckcode_image_path = settings.json_restore_path + '/yunnan/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.id = None
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://gsxt.ynaic.gov.cn/notice/',
				'searchList':'http://gsxt.ynaic.gov.cn/notice/search/ent_info_list',
				'validateCode':'http://gsxt.ynaic.gov.cn/notice/captcha?preset=&ra=0.06570781518790503'}
	
		self.one_dict = {u'基本信息':'ind_comm_pub_reg_basic',
				u'股东信息':'ind_comm_pub_reg_shareholder',
				u'发起人信息':'ind_comm_pub_reg_shareholder',
				u'股东（发起人）信息':'ind_comm_pub_reg_shareholder',
				u'变更信息':'ind_comm_pub_reg_modify',
				u'主要人员信息':'ind_comm_pub_arch_key_persons',
				u'分支机构信息':'ind_comm_pub_arch_branch',
				u'清算信息':'ind_comm_pub_arch_liquidation',
				u'动产抵押登记信息':'ind_comm_pub_movable_property_reg',
				u'股权出置登记信息':'ind_comm_pub_equity_ownership_reg',
				u'股权出质登记信息':'ind_comm_pub_equity_ownership_reg',
				u'行政处罚信息':'ind_comm_pub_administration_sanction',
				u'经营异常信息':'ind_comm_pub_business_exception',
				u'严重违法信息':'ind_comm_pub_serious_violate_law',
				u'抽查检查信息':'ind_comm_pub_spot_check'}

		self.two_dict = {u'企业年报':'ent_pub_ent_annual_report',
				u'企业投资人出资比例':'ent_pub_shareholder_capital_contribution',
				u'股东（发起人）及出资信息':'ent_pub_shareholder_capital_contribution',
				u'股东及出资信息（币种与注册资本一致）':'ent_pub_shareholder_capital_contribution',
				u'股权变更信息':'ent_pub_equity_change',
				u'行政许可信息':'ent_pub_administration_license',
				u'知识产权出资登记':'ent_pub_knowledge_property',
				u'知识产权出质登记信息':'ent_pub_knowledge_property',
				u'行政处罚信息':'ent_pub_administration_sanction',
				u'变更信息':'ent_pub_shareholder_modify'}
		self.three_dict = {u'行政许可信息':'other_dept_pub_administration_license',
				u'行政处罚信息':'other_dept_pub_administration_sanction'}
		self.four_dict = {u'股权冻结信息':'judical_assist_pub_equity_freeze',
				u'司法股权冻结信息':'judical_assist_pub_equity_freeze',
				u'股东变更信息':'judical_assist_pub_shareholder_modify',
				u'司法股东变更登记信息':'judical_assist_pub_shareholder_modify'}
		self.result_json_dict = {}

	def get_check_num(self):
		resp = self.reqst.get(self.mydict['search'])
		if resp.status_code != 200:
			return None
		first = resp.content.find('session.token":')
		session_token = resp.content[first+17:first+53]

		resp = self.reqst.get(self.mydict['validateCode'])
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		with open('s.jpg', 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('yunnan')
		ck_code = code_cracker.predict_result('s.jpg')
		return ck_code[1],session_token

	def get_id_num(self, findCode):
		count = 0
		while count < 10:
			check_num,session_token = self.get_check_num()
			print check_num
			data = {'searchType':'1','captcha':check_num, "session.token": session_token, 'condition.keyword':findCode}
			resp = self.reqst.post(self.mydict['searchList'],data=data)
			if resp.status_code != 200:
				print resp.status_code
				print 'error...(get_id_num)'
				count += 1
				continue
			else:
				soup = BeautifulSoup(resp.content).find_all('div', attrs={'class':'link'})[0]
				hrefa = soup.find('a', attrs={'target':'_blank'})
				if hrefa:
					return hrefa['href'].split('&')[0]
				else:
					count += 1
					continue

	def get_tables(self, url):
		resp = self.reqst.get(url)
		if resp.status_code == 200:
			return BeautifulSoup(resp.content, 'html5lib').find_all('table')
			#return [table for table in tables] #if (table.find_all('th') or table.find_all('a')) ]
	def get_head_ths_tds(self, table):
		head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
		allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
		if head == u'股东信息' or head == u'发起人信息' or head == u'股东（发起人）信息':
			tdlist = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					tddict = {}
					detail_head, detail_allths, detail_alltds = self.get_head_ths_tds(self.get_tables(td.a['href'])[0])
					print '---------------------------', len(detail_allths[:3]+detail_allths[5:]), len(detail_alltds)
					tddict = self.get_one_to_one_dict(detail_allths[:3]+detail_allths[5:], detail_alltds)
					tdlist.append(tddict)
				elif td.get_text():
					tdlist.append(td.get_text().strip())
				else:
					tdlist.append(None)
			return head, allths, tdlist
			pass
		elif head == u'企业年报':
			tdlist = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					tddict = {}
					for table in self.get_tables(td.a['href']):
						enter_head, enter_allths, enter_alltds = self.get_head_ths_tds(table)
						print enter_head
						tddict[enter_head] = self.get_one_to_one_dict(enter_allths, enter_alltds)
					tdlist.append(tddict)
				elif td.get_text():
					tdlist.append(td.get_text().strip())
				else:
					tdlist.append(None)
			return head, allths, tdlist			
			pass
		else:
			if table.find_all('td') :
				alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
			else:
				alltds = [None for th in allths]
			if head == u'主要人员信息':
				return head, allths[:int(len(allths)/2)], alltds
			else:
				return head, allths, alltds
		#return (table.find_all('th')[0].get_text().strip().split('\n')[0].strip(), [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()], [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')])
	def get_one_to_one_dict(self, allths, alltds):
		if len(allths) == len(alltds):
			one_to_one_dict = {}
			for key, value in zip(allths, alltds):
				one_to_one_dict[key] = value
			return one_to_one_dict
		else:
			templist = []
			x = 0
			y = x + len(allths)
			#print '---------------------%d-------------------------------%d' % (len(allth), len(alltd))
			while y <= len(alltds):
				tempdict = {}
				for keys, values in zip(allths,alltds[x:y]):
					tempdict[keys] = values
				x = y
				y = x + len(allths)
				templist.append(tempdict)
			return templist

	def test_print_table(self, tables):
		for table in tables:
			print table
	def test_print_all_ths_tds(self, head, allths, alltds):
		print '--------------',head,'--------------'
		for th in allths:
			print th
		for td in alltds:
			print td
	def test_print_all_dict(self, mydict):
		for key,value in mydict.items():
			print key,':',value

	def get_json_one(self, mydict, tables):
		#self.test_print_table(tables)
		for table in tables:
			head, allths, alltds = self.get_head_ths_tds(table)
			print head
			self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
			#self.test_print_all_ths_tds(head, allths, alltds)
		pass			
	def get_json_two(self, mydict, tables):
		#self.test_print_table(tables)
		for table in tables:
			head, allths, alltds = self.get_head_ths_tds(table)
			print head
			self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		pass
	def get_json_three(self, mydict, tables):
		#self.test_print_table(tables)
		for table in tables:
			head, allths, alltds = self.get_head_ths_tds(table)
			print head
			self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		
		pass
	def get_json_four(self, mydict, tables):
		#self.test_print_table(tables)
		for table in tables:
			head, allths, alltds = self.get_head_ths_tds(table)
			print head
			self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		pass

	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		self.uuid = self.get_id_num(findCode)
		print self.uuid
		self.result_json_dict = {}

		tableone = self.get_tables(self.uuid + '&tab=01')
		self.get_json_one(self.one_dict, tableone)
		tabletwo = self.get_tables(self.uuid + '&tab=02')
		self.get_json_two(self.two_dict, tabletwo)
		tablethree = self.get_tables(self.uuid + '&tab=03')
		self.get_json_three(self.three_dict, tablethree)
		tablefour = self.get_tables(self.uuid + '&tab=06')
		self.get_json_four(self.four_dict, tablefour)

		CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	yunnan = YunnanCrawler('./enterprise_crawler/yunnan.json')
	yunnan.run('530000000002692')
	# f = open('enterprise_list/yunnan.txt', 'r')
	# for line in f.readlines():
	# 	print line.split(',')[2].strip()
	# 	yunnan.run(str(line.split(',')[2]).strip())
	# f.close()