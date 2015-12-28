# Program Rules

- 每个省份对应一个爬虫文件，代码格式如下：

        class ${Province}Clawer(object):     #请替换${Province}为省名，如BeiJing
        
            def run(self):
                pass
            
            ....

- settings.py 是所有爬虫的配置文件
- model 里面存放的是破解识别码需要的建模数据，每个省对应一个文件夹
- enterprise_list 里面放的是所有的企业名单，现在暂时是一个省一个文件，比如： beijing.txt
- CaptchaRecognition.py 是破解图片识别码的类，使用方法如下：

        from CaptchaRecognition import CaptchaRecognition
    
        recognition = CaptchaRecognition("beijing")  #support jiangshu etc
        result = recognition.predict_result(im_path)  # result is image code


## settings.py 说明


	#log
	log_level = logging.WARN
	log_file = '/data/clawer_result/enterprise/crawler.log'
	logger = None

	save_html = True   # 是否保存html
	html_restore_path = './enterprise_crawler'  #如果save_html为True，html存储在子目录下。子目录以省份命名。

	json_restore_path = './enterprise_crawler'   #最后结果转为json，输出到子目录下。子目录格式：${省份名}/${YEAR}/${MONTH}/ 。 每天一个文件，需要使用zlib压缩，文件名格式为； ${DAY}.json.gz 。 每行对应一个企业的JSON对象。

	enterprise_list_path = './enterprise_list/'  # 企业名单，每个省对应一个文件，如北京为beijing.txt

## 输出格式




## Beijing enterprise crawler 
----
####1. source code
(1) crawler.py contains several classes, they are:
>a)CrawlerUtils 
&nbsp;&nbsp;&nbsp;&nbsp;our tools class, there several useful functions which will be called frequently

>b)Crawler
&nbsp;&nbsp;&nbsp;&nbsp;our base crawler class


(2)hparser.py contains class Parser, the base class of a html page parser

(3)beijing_crawler.py contains class CrawlerBeijingEnt
&nbsp;&nbsp;&nbsp;&nbsp;CrawlerBeijingEnt is the derived class of Crawler, it crawls html page of beijing enterprise

(4) beijing_hparser.py contains class ParserBeijingEnt
&nbsp;&nbsp;&nbsp;&nbsp;ParserBeijingEnt is the derived class of hparser.Parser, it parses the html page of beijing enterprise


####2. work flow of crawler
(1) build a Crawler object (let's name it crawler) and a Parser objet(let's name it parser), crawler and parser is connected together by hoding reference of the other 
so we can access crawler in parser and access parser in crawler

(2) get the enterprise number 

(3) Crawler start work with enterprise number

(4) when crawler download a html page, our parser parse the html page to json data immediately

(5) when we download all relative html pages of a enterprise and parse them over to json data, we write the json data to file 

&nbsp;&nbsp;&nbsp;&nbsp;the crawl and parse process are work alternatively, instead of dividing them apart.
note that, a Crawler object corresponds a Parser object, they work in the same thread.

####3. run the program
&nbsp;&nbsp;&nbsp;&nbsp;there are some setting parameters in settings.py, we can change the program's behaviour by modifying the parameters

&nbsp;&nbsp;&nbsp;&nbsp;a key parameter is the crawler_num, because the crawler can run in multi-thread mode, this paramter denotes the thread number
to run our crawl and parse work. 

&nbsp;&nbsp;&nbsp;&nbsp;just execute run.py to start crawl and parse work

