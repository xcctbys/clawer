#encoding=utf-8
import json
import os

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser, Group

from clawer.models import MenuPermission, Clawer, ClawerTask,\
    ClawerTaskGenerator
from clawer.management.commands import task_generator_test, task_generator_run


class TestHomeViews(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client()
        
    def tearDown(self):
        TestCase.tearDown(self)
        
    def test_index(self):
        url = reverse("clawer.views.home.index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer_index(self):
        url = reverse("clawer.views.home.clawer")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer_all(self):
        url = reverse("clawer.views.home.clawer_all")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer_task_failed(self):
        url = reverse("clawer.views.home.clawer_task_failed")
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
        
        
class TestHomeApi(TestCase):
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
        
    def test_all(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        url = reverse("clawer.apis.home.clawer_all")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        
    def test_task_failed(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        clawer_generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print hello", cron="*", status=ClawerTaskGenerator.STATUS_PRODUCT)
        clawer_task = ClawerTask.objects.create(clawer=clawer, task_generator=clawer_generator, uri="http://github.com", status=ClawerTask.STATUS_FAIL)
        url = reverse("clawer.apis.home.clawer_task_failed")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        clawer_generator.delete()
        clawer_task.delete()
        
    def test_task(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        clawer_generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print hello", cron="*", status=ClawerTaskGenerator.STATUS_PRODUCT)
        clawer_task = ClawerTask.objects.create(clawer=clawer, task_generator=clawer_generator, uri="http://github.com", status=ClawerTask.STATUS_FAIL)
        url = reverse("clawer.apis.home.clawer_task")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        clawer_generator.delete()
        clawer_task.delete()
        
    def test_clawer_task_generator_update(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        code_path = "/tmp/test.py"
        code_file = open(code_path, "arw")
        code_file.write("print 'http://www.github.com'\n")
        code_file.close()
        code_file = open(code_path)
        url = reverse("clawer.apis.home.clawer_task_generator_update")
        
        resp = self.logined_client.post(url, data={"code_file":code_file, "clawer":clawer.id, "cron":"*"})
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        task_generator = ClawerTaskGenerator.objects.get(clawer=clawer)
        self.assertGreater(len(task_generator.code), 0)
        
        clawer.delete()
        task_generator.delete()
        os.remove(code_path)
        
    def test_clawer_task_generator_history(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        clawer_generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print hello", cron="*", status=ClawerTaskGenerator.STATUS_PRODUCT)
        url = reverse("clawer.apis.home.clawer_task_generator_history")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        clawer_generator.delete()
        
        
class TestCmd(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.user = DjangoUser.objects.create_user(username="xxx", password="xxx")
        self.group = Group.objects.create(name=MenuPermission.GROUPS[0])
        self.user.groups.add(self.group)

        
    def tearDown(self):
        TestCase.tearDown(self)
        self.user.delete()
        self.group.delete()
        
    def test_task_generator_test(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print 'TASK http://www.baidu.com'\nos.exit(2)\n", cron="*")
        
        ret = task_generator_test.test_alpha(generator)
        self.assertFalse(ret)
        
        new_generator = ClawerTaskGenerator.objects.get(id=generator.id)
        self.assertGreater(len(new_generator.failed_reason), 0)
        
        clawer.delete()
        generator.delete()
        
    def test_task_generator_run(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print 'TASK http://www.baidu.com'\n", cron="*")
        
        ret = task_generator_run.run(generator.id)
        self.assertTrue(ret)
        
        clawer.delete()
        generator.delete()