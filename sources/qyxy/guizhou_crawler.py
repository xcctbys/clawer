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
import json

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
	import settings_pro as settings
else:
	import settings

class GuizhouCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/guizhou/'
	ckcode_image_path = settings.json_restore_path + '/guizhou/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.cur_time = str(int(time.time()*1000))
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/guizhou/ckcode.jpg'
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://gsxt.gzgs.gov.cn/',
				'searchList':'http://gsxt.gzgs.gov.cn/search!searchSczt.shtml',
				'validateCode':'http://gsxt.gzgs.gov.cn/search!generateCode.shtml?validTag=searchImageCode&'}
	
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
				u'股东及出资信息':'ent_pub_shareholder_capital_contribution',
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
		# print self.mydict['search']
		resp = self.reqst.get(self.mydict['search'], timeout = 120)
		if resp.status_code != 200:
			print resp.status_code
			return None
		# print BeautifulSoup(resp.content).prettify
		resp = self.reqst.get(self.mydict['validateCode']+self.cur_time, timeout = 120)
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		# print self.ckcode_image_path
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('guizhou')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)

		with open('./down/'+ck_code[0]+'.jpg', 'wb') as f:
			f.write(resp.content)

		# return ck_code[1]
		if not ck_code is None:
			return ck_code[1]
		else:
			return None

		

	def get_id_num(self, findCode):
		count = 0
		while count < 20:
			# print self.cur_time
			yzm = self.get_check_num()
			print yzm
			if yzm is None:
				# print count,yzm
				count += 1
				continue
			data = {'q':findCode, 'validCode':yzm}
			resp = self.reqst.post(self.mydict['searchList'], data=data, timeout=120)

			if resp.status_code == 200 :
				result_dict = json.loads(resp.content)
				# print result_dict
				if result_dict[u'successed'] == 'true' or result_dict[u'successed'] == True:
					print result_dict
					return result_dict[u'data'][0][u'nbxh']
					break
				else:
					count += 1
					continue
			else:
				count+=1
				continue
			# print resp.content
			break
			count += 1
		pass
	

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

	def get_json_one(self, mydict, tables, *param):
		
		pass			
	def get_json_two(self, mydict, tables):
		
		
		pass
	def get_json_three(self, mydict, tables):
		
		pass
	def get_json_four(self, mydict, tables):
		pass

	def send_post(self, host, nbxh, c, t, out):
		count = 0
		while count < 10:
			data = {'nbxh':nbxh, 'c':c, 't':t}
			try:
				resp = self.reqst.post(host, data=data, timeout = out)
			except:
				count +=1
				continue
			if resp.status_code == 200:
				return resp.content
			else:
				count += 1
				continue


	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		nbxh = self.get_id_num(findCode)

		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '5', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '3', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '2', '3', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '8', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '36', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '9', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '25', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '4', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '1', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '33', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '34', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '35', 60)
		print result_dict


		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '13', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '40', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '23', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '20', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '21', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '22', 60)
		print result_dict

		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchOldData.shtml',nbxh, '0', '37', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchOldData.shtml',nbxh, '0', '38', 60)
		print result_dict


		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '49', 60)
		print result_dict
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '53', 60)
		print result_dict


		# CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	guizhou = GuizhouCrawler('./enterprise_crawler/guizhou.json')
	# guizhou.run('520200000002090')
	f = open('enterprise_list/guizhou.txt', 'r')
	for line in f.readlines():
		print line.split(',')[2].strip()
		guizhou.run(str(line.split(',')[2]).strip())
	f.close()