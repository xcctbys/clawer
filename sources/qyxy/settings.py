import logging
#log level
log_level = logging.DEBUG

#denote whether to save html page
save_html = True

html_restore_path = './enterprise_crawler'
json_restore_path = './enterprise_crawler'

#our enterprise list to be crawled
enterprise_list_path = './enterprise_list/beijing.txt'

#crawler num, for multi-thread crawl, if crawler_num is larger than 1, we may occur http 500 error possible
crawler_num = 3