# encoding=utf-8
"""此代码于本地环境运行，拉起浏览器模拟人工操作获取所需数据，每次运行需人工更改存放有url的txt文件文件名以及生成json文件文件名
"""
import json
import time
from selenium import webdriver


class Analysis(object):
    def __init__(self):
        self.textpath=r"test.txt"  # 读取url文本路径
        self.result = {"twittes_list": []}
        self.arr = []

    def get_url(self):
        text=open(self.textpath)
        for lines in text.readlines():
            lines=lines.replace("\n", "")
            self.arr.append(lines)
        text.close()

    def selenium_obtain(self):
        driver = webdriver.Firefox()
        for url in self.arr:
            driver.get(url)
            js = "var q=document.documentElement.scrollTop+=100000"  # 运用于firefox以及safari浏览器环境下（其他浏览器请改为js="var q=document.body.scrollTop+=100000"）
            for i in range(0, 5):  # 模拟网页下拉操作（循环5次）
                try:
                    driver.execute_script(js)  # 运行js
                    time.sleep(1)
                except:
                    break
            try:
                twittes_content = driver.find_elements_by_class_name("content")
            except:
                continue
            for each in twittes_content:
                try:
                    data = {}
                    twittes_time = each.find_element_by_class_name("tweet-timestamp")
                    twitte = each.find_element_by_class_name("js-tweet-text")
                    each_time = twittes_time.get_attribute("title")
                    data["time"] = each_time
                    data["twitte"] = twitte.text
                    self.result["twittes_list"].append(data)
                except:
                    continue
        driver.quit()


if __name__ == "__main__":

    sName = 'test.json'  # 需要写入json文件的文件名
    f = open(sName,'w+')

    analysis = Analysis()
    analysis.get_url()
    analysis.selenium_obtain()

    jsonStr = json.dumps(analysis.result)
    f.write(jsonStr)
    f.write('\n')
    f.close
