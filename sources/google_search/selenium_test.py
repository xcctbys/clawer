# encoding=utf-8
"""此代码于本地环境运行，拉起浏览器模拟人工操作获取所需数据
"""
import json
import time
from selenium import webdriver
import datetime

driver = webdriver.Firefox()

weekday = datetime.datetime.today().weekday()
if weekday < 2:
    starTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 12)).strftime("%Y-%m-%d")
    endTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 6)).strftime("%Y-%m-%d")
else:
    starTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 5)).strftime("%Y-%m-%d")
    endTime = (datetime.datetime.now() - datetime.timedelta(days=weekday - 1)).strftime("%Y-%m-%d")

sName = str(starTime) + "-" + str(endTime)
textpath = sName + ".txt"   # 读取的url文本
text = open(textpath)
arr = []
for lines in text.readlines():  # 依次读每一行并将其加入列表
    lines=lines.replace("\n", "")
    arr.append(lines)
text.close()

f = open(sName + ".json", 'w+')    # 写入的json文件
for url in arr:
    driver.get(url)
    time.sleep(3)
    driver.find_element_by_partial_link_text(u'工具').click()  # 模拟点击操作
    try:
        result = driver.find_element_by_id('resultStats').text
    except:
        time.sleep(1)   # 模拟点击获取数据失败后再次尝试
        driver.find_element_by_partial_link_text(u'工具').click()
        result = driver.find_element_by_id('resultStats').text  # 提取所需结果
    keyword = driver.title  # 提取关键词
    data = {}
    data["keyword"] = keyword
    data["result"] = result

    jsonStr = json.dumps(data)
    f.write(jsonStr)  # 将构造的json写入文件
    f.write('\n')
driver.quit()
f.close
