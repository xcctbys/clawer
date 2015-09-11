#encoding=utf-8
"""获得国内的所有城市三字码
http://airport.supfree.net/index.asp?page=284
"""

import urllib
import json



class Generator(object):
    MAX_PAGE = 284
    
    def __init__(self):
        self.base = "http://airport.supfree.net/index.asp"
    
    def page_url(self, page):
        return self.base + "?" + urllib.urlencode({"page":page})


if __name__ == "__main__":
    generator = Generator()
    
    for i in range(1, Generator.MAX_PAGE+1):
        data = {"uri": generator.page_url(i)}
        print json.dumps(data)