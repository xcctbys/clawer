#encoding=utf-8
from django.conf import settings


#whether to save html page
save_html = False

html_restore_path = './enterprise_crawler'
if hasattr(settings, 'ENTERPRISE_HTML_RESTORE_PATH'):
    html_restore_path = settings.ENTERPRISE_HTML_RESTORE_PATH
    

json_restore_path = './enterprise_crawler'
if hasattr(settings, 'ENTERPRISE_JSON_RESTORE_PATH'):
    json_restore_path = settings.ENTERPRISE_JSON_RESTORE_PATH
