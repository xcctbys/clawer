import logging

#log
log_level = logging.WARN
log_file = '/home/web_log/crawler.log'
logger = None

#whether to save html page
save_html = False

html_restore_path = '/data/clawer_result/enterprise/html'
json_restore_path = '/data/clawer_result/enterprise/json'

#our enterprise list to be crawled
enterprise_list_path = './enterprise_list/'

crawler_num = 3


#for sentry
sentry_open = False
sentry_dns = 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2'
sentry_client = None
