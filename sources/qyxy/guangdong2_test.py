import unittest
from Guangdong2 import Guangdong2


urls ={
        "main": "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_3au/If33vWye5UuPp+iY6u6FQtJGDUruMalngHz1ONi2UJ96uTS+QaKhmOwDSFMD-7kW54gFL28iQmsO8Qn3cTA==",
        "ind_comm_url" : "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_3au/If33vWye5UuPp+iY6u6FQtJGDUruMalngHz1ONi2UJ96uTS+QaKhmOwDSFMD-7kW54gFL28iQmsO8Qn3cTA==",
        "ent_pub_url" : "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html",
        "other_dept_pub_url": "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
        "judical_assist_url": "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html",
        }
class TestGuangdong2(unittest.TestCase):


    def setUp(self):
        self.guangdong = Guangdong2()

        self.crawler = self.guangdong.crawler
        self.analyser = self.guangdong.analysis
        page_entInfo = self.crawler.crawl_page_by_url(urls['main'])['page']
        self.post_data = self.analyser.parse_page_data_2(page_entInfo)
    def tearDown(self):
        self.guangdong = None
        self.post_data= None

    def test_run_crawl_ind_comm_pub_pages(self):
        data = self.crawler.crawl_ind_comm_pub_pages(urls['ind_comm_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_ent_pub_pages(self):
        data = self.crawler.crawl_ent_pub_pages(urls['ent_pub_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_other_dept_pub_pages(self):
        data = self.crawler.crawl_other_dept_pub_pages(urls['other_dept_pub_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

    def test_run_crawl_judical_assist_pub_pages(self):
        data = self.crawler.crawl_judical_assist_pub_pages(urls['judical_assist_url'],2, self.post_data)
        print data
        self.assertIsNotNone(data)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGuangdong2('test_run_crawl_ind_comm_pub_pages'))
    suite.addTest(TestGuangdong2('test_run_crawl_ent_pub_pages'))
    suite.addTest(TestGuangdong2('test_run_crawl_other_dept_pub_pages'))
    suite.addTest(TestGuangdong2('test_run_crawl_judical_assist_pub_pages'))

    return suite

if __name__ == "__main__":
    # method 1
    # unittest.main()
    # method 2
    # runner = unittest.TextTestRunner()
    # runner.run(suite())
    # method 3 , this method can be used to test several classes
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestGuangdong2)
    runner = unittest.TextTestRunner()
    runner.run(suite1)

