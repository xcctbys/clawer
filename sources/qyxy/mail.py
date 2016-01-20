#encoding=utf-8

import smtplib


class SendMail(object):
    
    def __init__(self, host, port, username, password, ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.smtp = None
    
    def send(self, from_addr, to_addrs, subject, content):
        self._login()
        
        msg = u"From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_addr, ", ".join(to_addrs), subject)
        msg += content

        self.smtp.sendmail(from_addr, to_addrs, msg)
        self.smtp.quit()
    
    def _login(self):
        if self.ssl:
            self.smtp = smtplib.SMTP_SSL(self.host, self.port)
        else:
            self.smtp = smtplib.SMTP(self.host, self.port)
            
        self.smtp.connect(self.host, self.port)
        self.smtp.login(self.username, self.password)
        