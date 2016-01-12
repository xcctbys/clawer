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
import time

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
	import settings_pro as settings
else:
	import settings

class SichuanCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/sichuan/'
	ckcode_image_path = settings.json_restore_path + '/sichuan/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.pripid = None
		self.cur_time = str(int(time.time()*1000))
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/sichuan/ckcode.jpg'
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://gsxt.scaic.gov.cn/ztxy.do?method=index&random=',
				'searchList':'http://gsxt.scaic.gov.cn/ztxy.do?method=list&djjg=&random=',
				'validateCode':'http://gsxt.scaic.gov.cn/ztxy.do?method=createYzm'}
	
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
		print self.mydict['search']+self.cur_time
		resp = self.reqst.get(self.mydict['search']+self.cur_time)
		if resp.status_code != 200:
			print resp.status_code
			return None
		#print BeautifulSoup(resp.content).prettify
		resp = self.reqst.get(self.mydict['validateCode']+'&dt=%s&random=%s' % (self.cur_time, self.cur_time))
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('sichuan')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)
		return ck_code[1]

		

	def get_id_num(self, findCode):
		yzm = self.get_check_num()
		print self.cur_time
		data = {'currentPageNo':'1', 'yzm':yzm, 'cxym':"cxlist", 'maent.entname':findCode}
		resp = self.reqst.post(self.mydict['searchList']+self.cur_time, data=data)
		print resp.status_code
		divs = BeautifulSoup(resp.content).find_all('div', attrs={"style":"width:950px; padding:25px 20px 0px; overflow: hidden;float: left;"})
		#print divs[0]
		try:
			return divs[0].ul.li.a['onclick'][10:26]
		except:
			print '*'*100
			pass
		#print BeautifulSoup(resp.content).prettify

		data = {'method':'qyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk1', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		print resp.status_code
		for table in BeautifulSoup(resp.content).find_all('table'):
			print table
		# data = {'method':'baInfo', 'maent.pripid':self.pripid, 'czmk':'czmk2', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'dcdyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'gqczxx', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'jyycInfo', 'maent.pripid':self.pripid, 'czmk':'czmk6', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'yzwfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk14', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'cfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk3', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code
		# data = {'method':'ccjcInfo', 'maent.pripid':self.pripid, 'czmk':'czmk7', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# print resp.status_code

		


		pass
	def get_re_list_from_content(self, content):
		
		pass

	
		
	def get_head_ths_tds(self, table):
		head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
		allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
		# if head == u'股东信息' or head == u'发起人信息' or head == u'股东（发起人）信息' or head == u'行政许可信息':
		# 	tdlist = []
		# 	for td in table.find_all('td'):
		# 		if td.find_all('a'):
		# 			tddict = {}
		# 			try:
		# 				detail_head, detail_allths, detail_alltds = self.get_head_ths_tds(self.get_tables(td.a['href'])[0])
		# 			except:
		# 				pass
		# 			if detail_head == u'股东及出资信息':
		# 				detail_content = self.reqst.get(td.a['href']).content
		# 				detail_alltds = self.get_re_list_from_content(detail_content)
		# 			#print '---------------------------', len(detail_allths[:3]+detail_allths[5:]), len(detail_alltds)
		# 			tddict = self.get_one_to_one_dict(detail_allths[:3]+detail_allths[5:], detail_alltds)
		# 			tdlist.append(tddict)
		# 		elif td.get_text():
		# 			tdlist.append(td.get_text().strip())
		# 		else:
		# 			tdlist.append(None)
		# 	return head, allths, tdlist
		# 	pass
		# elif head == u'股东及出资信息（币种与注册资本一致）' or head == u'股东及出资信息':
		# 	pass
		if head == u'企业年报':
			tdlist = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					tddict = {}
					for i, table in enumerate(self.get_tables(td.a['href'])):
						enter_head, enter_allths, enter_alltds = self.get_head_ths_tds(table)
						#print enter_head
						if i==0:
							enter_head = enter_allths[0]
							enter_allths = enter_allths[1:]
						#self.test_print_all_ths_tds(enter_head, enter_allths, enter_alltds)
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
		pass
		#return (table.find_all('th')[0].get_text().strip().split('\n')[0].strip(), [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()], [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')])
	def get_one_to_one_dict(self, allths, alltds):
		pass

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
	def get_table_by_head(self, tables, head_item):
		for table in tables:
			if table.find_all('th'):
				temp_head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
				print 'temp_head', temp_head
				if temp_head == head_item:
					return table
		else:
			print 'no'*10
		pass

	def get_json_one(self, mydict, tables, *param):
		#self.test_print_table(tables)
		for head_item in param:
			print '----'*10, head_item
			table = self.get_table_by_head(tables, head_item)
			if table:
				head, allths, alltds = self.get_head_ths_tds(table)
				self.test_print_all_ths_tds(head, allths, alltds)
		pass			
	def get_json_two(self, mydict, tables):
		#self.test_print_table(tables)
		
		pass
	def get_json_three(self, mydict, tables):
		#self.test_print_table(tables)
		
		
		pass
	def get_json_four(self, mydict, tables):
		#self.test_print_table(tables)
		pass

	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		self.pripid = self.get_id_num(findCode)
		print findCode, self.pripid

		data = {'method':'qyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk1', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		print BeautifulSoup(resp.content).prettify
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'股东信息', u'基本信息', u'变更信息')

		# data = {'method':'dcdyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		# data = {'method':'gqczxx', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		# data = {'method':'jyycInfo', 'maent.pripid':self.pripid, 'czmk':'czmk6', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		# data = {'method':'yzwfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk14', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		# data = {'method':'cfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk3', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		# data = {'method':'ccjcInfo', 'maent.pripid':self.pripid, 'czmk':'czmk7', 'random':self.cur_time}
		# resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data)
		# self.get_json_one(self.one_dict, BeautifunSoup(resp.content).find_all('table'), u'', u'', u'')

		self.result_json_dict = {}

		

		#CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	sichuan = SichuanCrawler('./enterprise_crawler/sichuan.json')
	sichuan.run('510708000002128')
	# sichuan.run('511000000000753')
	# sichuan.run('510300000004462')
	# f = open('enterprise_list/sichuan.txt', 'r')
	# for line in f.readlines():
	# 	print line.split(',')[2].strip()
	# 	sichuan.run(str(line.split(',')[2]).strip())
	# f.close()