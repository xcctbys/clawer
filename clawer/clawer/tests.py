#encoding=utf-8
import json
import os
import datetime
import logging

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser, Group

from clawer.models import MenuPermission, Clawer, ClawerTask,\
    ClawerTaskGenerator, ClawerAnalysis, ClawerAnalysisLog, Logger,\
    ClawerDownloadLog
from clawer.management.commands import task_generator_test, task_generator_run, task_analysis, task_analysis_merge, task_dispatch
from clawer.utils import UrlCache, Download


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
        
    def test_clawer_download_log(self):
        url = reverse("clawer.views.home.clawer_download_log")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer_analysis_log(self):
        url = reverse("clawer.views.home.clawer_analysis_log")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_clawer_setting(self):
        url = reverse("clawer.views.home.clawer_setting")
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


  

class TestLoggerApi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client()
        
    def test_index(self):
        logger = Logger.objects.create(title="xxx", content="xxx", from_ip="127.0.0.1")
        url = reverse("clawer.apis.logger.all")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        logger.delete()
                
        
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
        
    def test_download_log(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        clawer_generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print hello", cron="*", status=ClawerTaskGenerator.STATUS_PRODUCT)
        clawer_task = ClawerTask.objects.create(clawer=clawer, task_generator=clawer_generator, uri="http://github.com", status=ClawerTask.STATUS_FAIL)
        download_log = ClawerDownloadLog.objects.create(clawer=clawer, task=clawer_task)
        url = reverse("clawer.apis.home.clawer_download_log")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        clawer_generator.delete()
        clawer_task.delete()
        download_log.delete()
        
    def test_task(self):
        UrlCache(None).flush()
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
    
    def test_task_add(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        url = reverse("clawer.apis.home.clawer_task_add")
        
        resp = self.logined_client.post(url, {"clawer":clawer.id, "uri":"http://www.1.com"})
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        
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
        
    def test_clawer_analysis_update(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        code_path = "/tmp/test.py"
        code_file = open(code_path, "arw")
        code_file.write("print 'http://www.github.com'\n")
        code_file.close()
        code_file = open(code_path)
        url = reverse("clawer.apis.home.clawer_analysis_update")
        
        resp = self.logined_client.post(url, data={"code_file":code_file, "clawer":clawer.id})
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        analysis = ClawerAnalysis.objects.get(clawer=clawer)
        self.assertGreater(len(analysis.code), 0)
        
        clawer.delete()
        analysis.delete()
        os.remove(code_path)
    
    def test_clawer_analysis_history(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code="print")
        url = reverse("clawer.apis.home.clawer_analysis_history")
        
        resp = self.logined_client.get(url, {"clawer_id":clawer.id})
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        analysis.delete()
        
    def test_clawer_analysis_log(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code="print")
        task_generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="sss", cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=task_generator, uri="http://www.csdn.net")
        analysis_log = ClawerAnalysisLog.objects.create(clawer=clawer, analysis=analysis, task=task)
        url = reverse("clawer.apis.home.clawer_analysis_log")
        
        resp = self.logined_client.get(url)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer.delete()
        analysis.delete()
        analysis_log.delete()
        
    def test_clawer_setting_update(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        url = reverse("clawer.apis.home.clawer_setting_update")
        data = {"dispatch":10, "analysis":90, "clawer":clawer.id}
        
        resp = self.logined_client.post(url, data)
        result = json.loads(resp.content)
        self.assertTrue(result["is_ok"])
        
        clawer_setting = clawer.settings()
        self.assertEqual(clawer_setting.dispatch, data["dispatch"])
        
        clawer.delete()
        
        
        
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
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print '{\"uri\": \"http://www.github.com\"}'\nos.exit(2)\n", cron="*")
        
        ret = task_generator_test.test_alpha(generator)
        self.assertFalse(ret)
        
        new_generator = ClawerTaskGenerator.objects.get(id=generator.id)
        self.assertGreater(len(new_generator.failed_reason), 0)
        
        clawer.delete()
        generator.delete()
        
    def test_task_generator_run(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print '{\"uri\": \"http://www.github.com\"}'\n", cron="*", status=ClawerTaskGenerator.STATUS_ON)
        product_path = generator.product_path()
        if os.path.exists(product_path):
            os.remove(product_path)
        
        ret = task_generator_run.run(generator.id)
        self.assertTrue(ret)
        
        clawer.delete()
        generator.delete()
        
    def test_task_dispatch(self):
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print '{\"uri\": \"http://www.gitsdhub.com\"}'\n", cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=generator, uri="https://www.ba90idu.com")
        
        q = task_dispatch.run()
        self.assertEqual(len(q.jobs), 1)
        
        clawer.delete()
        generator.delete()
        task.delete()
        
    def test_task_analysis(self):
        UrlCache(None).flush()
        path = "/tmp/ana.store"
        tmp_file = open(path, "w")
        tmp_file.write("hi")
        tmp_file.close()
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print '{\"uri\": \"http://www.gith23ub.com\"}'\n", cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=generator, uri="https://www.ba56idu.com", store=path, status=ClawerTask.STATUS_SUCCESS)
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code="print '{\"url\":\"ssskkk\"}'\n")
        
        task_analysis.do_run()
        analysis_log = ClawerAnalysisLog.objects.filter(clawer=clawer, analysis=analysis, task=task).order_by("-id")[0]
        print "analysis log failed reason: %s" % analysis_log.failed_reason
        self.assertEqual(analysis_log.status, ClawerAnalysisLog.STATUS_SUCCESS)
        
        clawer.delete()
        generator.delete()
        task.delete()
        analysis.delete()
        analysis_log.delete()
        os.remove(path)
        
    def test_task_analysis_with_exception(self):
        UrlCache(None).flush()
        path = "/tmp/ana.store"
        tmp_file = open(path, "w")
        tmp_file.write("hi")
        tmp_file.close()
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print a", cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=generator, uri="https://www.baweidu.com", store=path, status=ClawerTask.STATUS_SUCCESS)
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code="print a\n")
        
        task_analysis.do_run()
        analysis_log = ClawerAnalysisLog.objects.filter(clawer=clawer, analysis=analysis, task=task).order_by("-id")[0]
        print "analysis log failed reason: %s" % analysis_log.failed_reason
        self.assertEqual(analysis_log.status, ClawerAnalysisLog.STATUS_FAIL)
        
        clawer.delete()
        generator.delete()
        task.delete()
        analysis.delete()
        analysis_log.delete()
        os.remove(path)
        
    def test_task_analysis_with_large(self):
        path = "/tmp/ana.store"
        tmp_file = open(path, "w")
        tmp_file.write("hi")
        tmp_file.close()
        code = "import json\nresult={}\nfor i in range(100000):\n    result[i] = 'test'\nprint json.dumps(result)"
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code=code, cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=generator, uri="https://www.baidu.com", store=path, status=ClawerTask.STATUS_SUCCESS)
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code=code)
        
        task_analysis.do_run()
        analysis_log = ClawerAnalysisLog.objects.filter(clawer=clawer, analysis=analysis, task=task).order_by("-id")[0]
        print "analysis log failed reason: %s" % analysis_log.failed_reason
        self.assertEqual(analysis_log.status, ClawerAnalysisLog.STATUS_SUCCESS)
        
        clawer.delete()
        generator.delete()
        task.delete()
        analysis.delete()
        analysis_log.delete()
        os.remove(path)
        
    def test_task_analysis_merge(self):
        pre_hour = datetime.datetime.now() - datetime.timedelta(minutes=60)
        clawer = Clawer.objects.create(name="hi", info="good")
        generator = ClawerTaskGenerator.objects.create(clawer=clawer, code="print '{\"uri\": \"http://www.github111.com\"}'\n", cron="*")
        task = ClawerTask.objects.create(clawer=clawer, task_generator=generator, uri="https://www.baid11u.com")
        analysis = ClawerAnalysis.objects.create(clawer=clawer, code="print '{\"url\":\"ssskkk\"}'\n")
        analysis_log = ClawerAnalysisLog.objects.create(clawer=clawer, analysis=analysis, task=task, status=ClawerAnalysisLog.STATUS_SUCCESS, 
                                                        result=json.dumps({"hi":"ok"}), add_datetime=pre_hour)
        
        task_analysis_merge.run()
        
        clawer.delete()
        generator.delete()
        task.delete()
        analysis.delete()
        analysis_log.delete()
        

class TestDownload(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        
    def test_selenium(self):
        url = "http://blog.sina.com.cn/s/blog_6175bf700102w08a.html?tj=1"
        downloader = Download(url, engine=Download.ENGINE_SELENIUM)
        downloader.download()
        logging.debug(u"%s", downloader.content)
        print downloader.spend_time
        self.assertIsNotNone(downloader.content)