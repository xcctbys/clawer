# Beijing enterprise crawler 
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

