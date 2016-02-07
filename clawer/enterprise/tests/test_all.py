#encoding=utf-8
from django.test.testcases import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from django.test.client import Client
from enterprise.models import Enterprise, Province
import json
import os
from enterprise.utils import EnterpriseDownload


class TestApis(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        self.user = DjangoUser.objects.create_user(username="go", password='go')
        self.client = Client()
        self.client.login(username=self.user.username, password=self.user.username)
        
    def tearDown(self):
        TestCase.tearDown(self)
        self.user.delete()
        
    def test_get_all(self):
        url = reverse('enterprise.apis.get_all')
        enterprise = Enterprise.objects.create(name="kkk", register_no="kkkk00991", province=Province.ANHUI)
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        enterprise.delete()
        
    def test_add(self):
        path = "/tmp/names.csv"
        with open(path, "w") as f:
            names = u""
            names += u"kkkk,安徽,2233"
            names += u"kkkk,anhui,2233"
            names += u"kkkk,anhui,2233"
            names += u"2233,anhui,3344"
            f.write(names.encode("utf-8"))
        
        f = open(path)
        url = reverse("enterprise.apis.add")
        resp = self.client.post(url, {'names_file': f})
        self.assertEqual(resp.status_code, 200)
        
        result = json.loads(resp.content)
        self.assertGreater(result["success"], 0)
        
        os.remove(path)
        

class TestViews(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        self.user = DjangoUser.objects.create_user(username="go", password='go')
        self.client = Client()
        self.client.login(username=self.user.username, password=self.user.username)
        
    def tearDown(self):
        TestCase.tearDown(self)
        self.user.delete()
        
    def test_get_all(self):
        url = reverse('enterprise.views.get_all')
        enterprise = Enterprise.objects.create(name="kkk", register_no="kkkk00991", province=Province.BEIJING)
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        enterprise.delete()
        

class TestEnterpriseDownload(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
    
    def test_run(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.BEIJING), u"北京高华证券有限责任公司", u'110000007552812')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)
        