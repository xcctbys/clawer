#encoding=utf-8
import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser, Group
from clawer.models import MenuPermission


class TestViews(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client()
        
    def tearDown(self):
        TestCase.tearDown(self)
        
    def test_index(self):
        url = reverse("clawer.views.index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer(self):
        url = reverse("clawer.views.clawer")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        


class TestUserApi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.user = DjangoUser.objects.create_user(username="xxx", password="xxx")
        self.group = Group.objects.create(name=MenuPermission.GROUPS[0])
        self.user.groups.add(self.group)
        self.client = Client()
        self.logined_client = Client()
        self.logined_client.login(username=self.user.username, password=self.user.username)
        
    def tearDown(self):
        TestCase.tearDown(self)
        self.user.delete()
        self.group.delete()
        
    def test_login(self):
        data = {"username":"xxx", "password":"kkkk"}
        url = reverse("clawer.apis.user.login")
        
        resp = self.client.get(url, data)
        result = json.loads(resp.content)
        self.assertFalse(result["is_ok"])
        
    def test_is_logined(self):
        url = reverse("clawer.apis.user.is_logined")
        
        resp = self.client.get(url)
        result = json.loads(resp.content)
        self.assertFalse(result["is_ok"])
        
    def test_keepalive(self):
        url = reverse("clawer.apis.user.keepalive")
        
        resp = self.client.get(url)
        result = json.loads(resp.content)
        self.assertFalse(result["is_ok"])
        
    def test_logout(self):
        url = reverse("clawer.apis.user.logout")
        
        resp = self.client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
    def test_get_my_menus(self):
        url = reverse("clawer.apis.user.get_my_menus")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        