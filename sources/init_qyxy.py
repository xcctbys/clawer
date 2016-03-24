#coding:utf8

class History(object):

	def __init__(self):
		self.total_page = [0 for i in range(PROVINCE_NUM)]
		self.current_page = [0 for i in range(PROVINCE_NUM)]
		self.flag = 1
		self.path = "/tmp/qyxy"

	def load(self):
		if os.path.exists(self.path) is False:
			return

		with open(self.path, "r") as f:
			old = pickle.load(f)
			self.total_page = old.total_page
			self.current_page = old.current_page

	def save(self):
		with open(self.path, "w") as f:
			pickle.dump(self, f)

a = History()
a.save()