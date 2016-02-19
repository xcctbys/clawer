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

    def test_run_xizang(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.XIZANG), u"西藏同信证券股份有限公司", u'5400001000374')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_shanghai(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.SHANGHAI), u"海通证券股份有限公司", u'310000000016182')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_zongju(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.ZONGJU), u"中信证券股份有限公司", u'100000000018305')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_heilongjiang(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.HEILONGJIANG), u"江海证券有限公司", u'230100100019556')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_jiangsu(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.JIANGSU), u"华泰证券股份有限公司", u'320000000000192')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_shanxi(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.SHANXI), u"山西证券股份有限公司", u'140000100003883')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    """
    def test_run_tianjin(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.TIANJIN), u"融创房地产集团有限公司", u'120111000006866')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_shandong(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.SHANDONG), u"中泰证券股份有限公司", u'370000018067809')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_zhejiang(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.ZHEJIANG), u"万向钱潮股份有限公司", u'330000000050426')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_xinjiang(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.XINJIANG), u"中建西部建设股份有限公司", u'650000040000136')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_chongqing(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.CHONGQING), u"中房地产股份有限公司", u'500000000006873')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_yunnan(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.YUNNAN), u"云南三七科技有限公司", u'530000000010908')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_henan(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.HENAN), u"中信重工机械股份有限公司", u'410300110053941')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)


    def test_run_shaanxi(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.SHAANXI), u"西部证券股份有限公司", u'610000100026931')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_jilin(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.JILIN), u"东北证券股份有限公司", u'220000000005183')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)

    def test_run_hainan(self):
        url = u"enterprise://%s/%s/%s/" % (Province.to_name(Province.HAINAN), u"万和证券有限责任公司", u'460000000091050')
        downloader = EnterpriseDownload(url)
        data = downloader.download()
        self.assertIsNotNone(data)
    """


