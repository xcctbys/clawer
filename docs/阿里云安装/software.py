#coding=utf-8

import os



from fabric.api import run, sudo
from fabric.api import env
from fabric.api import roles
from fabric.api import local
from fabric.api import put
from fabric.api import cd
from fabric.contrib import files




        

class Installer(object):

    @classmethod
    def default(cls):
        return cls()

    def __init__(self):
        self.douban_pip = "https://pypi.douban.com/simple/"
        self.python = "/usr/local/python27/bin/python"
        self.easy_install = "/usr/local/python27/bin/easy_install"
        self.virtualenv = "/usr/local/python27/bin/virtualenv"
        self.django14 = "/home/virtualenvs/py27"
        self.django14_pip = os.path.join(self.django14, "bin", "pip")
        self.django14_python = os.path.join(self.django14, "bin", "python")
        self.django18 = "/home/virtualenvs/dj18"
        self.django18_pip = os.path.join(self.django18, "bin", "pip")
        self.django18_python = os.path.join(self.django18, "bin", "python")
        self.web_log = "/home/web_log"
        self.system_libs = ["zlib-devel", 
            "pcre-devel", 
            "openssl-devel", 
            "bzip2-devel", 
            "curl", 
            "curl-devel", 
            "libjpeg-turbo-devel", 
            "freetype-devel", 
            "mysql", 
            "mysql-libs", 
            "mysql-devel", 
            "git", 
            "cyrus-sasl", 
            "cyrus-sasl-devel",
            "gcc",
            "gcc-c++",
            "gcc-gfortran",
            "nodejs",
            "npm",
            "bzip2",
            "xorg-x11-server-Xvfb",
            'libxslt-devel', 
            'libxml2-devel', 
            'libffi-devel',
            "lapack-devel",
            "blas-devel",
            "gcc-gfortran",
            "gcc",
            "gcc-c++",
            "atlas-devel", 
            "zip",
            "unzip",
            "numpy",
            "scipy",
        ]
        self.system_apps = ["memcached", 
            "redis",
        ]

    def install_key(self):
        #install local public keys
        local("cp -f id_rsa ~/.ssh/")
        local("cat id_rsa.pub>~/.ssh/authorized_keys2")
        local("chmod -R 700 ~/.ssh")
        local("chmod 0600 ~/.ssh/id_rsa")
        #upload key files to remote
        put("id_rsa", "/tmp/")
        put("id_rsa.pub", "/tmp/")
        #change remote key files permission of myself and root
        run("if [ ! -d ~/.ssh ]; then\n cd && mkdir -p .ssh\n fi ")
        run("cp /tmp/id_rsa ~/.ssh/id_rsa")
        run("cat /tmp/id_rsa.pub > ~/.ssh/authorized_keys2")
        run("chmod -R 700 ~/.ssh")
        run("chmod 600 ~/.ssh/id_rsa")
        #for root
        sudo("if [ ! -d ~/.ssh ]; then\n cd /root && mkdir -p .ssh\n fi ")
        sudo("cp /tmp/id_rsa ~/.ssh/id_rsa")
        sudo("cat /tmp/id_rsa.pub > ~/.ssh/authorized_keys2")
        sudo("chmod -R 700 ~/.ssh")
        sudo("chmod 600 ~/.ssh/id_rsa")

    def install_env(self):
        """ run first
        """
        self.install_system_libs()
        self.install_system_apps()

        if files.exists(self.web_log) is False:
            sudo("mkdir %s" % self.web_log)

        self.install_python()

            

    def install_python(self):
        pytgz = "Python-2.7.6.tgz"

        if files.exists("/tmp/"+pytgz) is False:
            put(pytgz, "/tmp")

        if files.exists(self.python, True) is False:    
            sudo("cp /tmp/%s /root/" % pytgz)
            sudo("cd /root/ && tar -zxf Python-2.7.6.tgz && cd Python-2.7.6 && ./configure --prefix=/usr/local/python27 && make && make install")

        if files.exists(self.easy_install) is False:
            put("setuptools-3.3.zip", "/root", True)
            sudo("cd && unzip setuptools-3.3.zip && cd setuptools-3.3 && /usr/local/python27/bin/python setup.py install")
            sudo("%s pip" % self.easy_install)
            sudo("%s virtualenv" % self.easy_install)

    def install_system_libs(self):
        for lib in self.system_libs:
            sudo("yum install -y %s" % lib)

        sudo('yum groupinstall -y "X Window System"')
        sudo('yum groupinstall -y "Desktop"')
        sudo('yum groupinstall -y "Chinese Support"')
        sudo('yum install -y tigervnc-server')
        sudo('yum install -y firefox')

    def install_system_apps(self):

        for app in self.system_apps:
            sudo("yum install -y %s" % app)

    def install_phantomjs(self):
        sudo("npm install -g cnpm --registry=https://registry.npm.taobao.org")
        sudo("npm install -g phantomjs")


    def install_sysctl(cls):
        params = [
            "net.ipv4.tcp_max_tw_buckets=40000",
            "net.core.somaxconn=40000",
            "net.ipv4.tcp_tw_recycle=1",
            "net.ipv4.tcp_tw_reuse=1",
            "net.ipv4.tcp_fin_timeout=30",
        ]

        for param in params:
            sudo("sysctl %s" % param)
            param_name = param.split("=")[0]
            sudo("sed -i \"/%s/d\" /etc/sysctl.conf" % param_name)
            sudo("sed -i \"$ a %s\" /etc/sysctl.conf" % param)

    def install_django14(self):
        py_packages = [
            "python-memcached", 
            "python-crontab", 
            "Markdown", 
            "south", 
            "six", 
            "raven", 
            "pillow", 
            "MySQL-python", 
            "requests", 
            "uwsgi", 
            "redis", 
            "threadpool", 
            'python-crontab',
            'raven',
            'beautifulsoup4',
            'selenium',
            'rq',
            "supervisor",
            "Django==1.4.22",
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "django-smtp-ssl",
            "chardet",
            'jinja2',
        ]

        if files.exists(self.django14, True) is False:
            sudo("%s %s" % (self.virtualenv, self.django14))

        for pkg in py_packages:
            sudo("%s install %s" % (self.django14_pip ,pkg))

        

    def install_django18(self):
        py_packages = [
            "python-memcached", 
            "Markdown", 
            "raven", 
            "pillow",
            "MySQL-python", 
            "requests", 
            "uwsgi", 
            "redis", 
            "threadpool", 
            'python-crontab',
            'raven',
            'html5lib',
            'beautifulsoup4',
            'selenium',
            'rq',
            "supervisor",
            "django-smart-autoregister",
            "Cython",
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "Django==1.8.5",
            "gunicorn",
            "greenlet",
            "eventlet",
            "gevent",
            "django-smtp-ssl",
            'nltk',
            'jieba',
            'nose',
            'flake8',
            'jinja2',
        ]

        if files.exists(self.django18, True) is False:
            sudo("%s %s" % (self.virtualenv, self.django18))

        for pkg in py_packages:
            sudo("%s install %s" % (self.django18_pip, pkg))

        

    def install_haproxy(self):
        sudo("yum install -y haproxy")
        sudo("chkconfig haproxy on")
        sudo("cd /etc/haproxy && rm haproxy.cfg && ln -s /home/webapps/devops/haproxy/haproxy.cfg")
        sudo("service haproxy restart")

    def install_nginx(self):
        sudo("yum install -y nginx")
        sudo("chkconfig nginx on")
        sudo("cd /etc/nginx/ && mv nginx.conf nginx.conf.bak && ln -s /home/webapps/devops/nginx/nginx.conf")
        sudo("service nginx restart")    

    def install_sentry(self):
    	SENTRY_HOME="/home/virtualenvs/sentry"
    	python_libs=["sentry", "supervisor", "raven", "MySQL-python", "redis", "python-memcached", "django-smtp-ssl"]
    	system_libs="bzip2 bzip2-devel postgresql-devel"

        sudo("yum install -y %s" % system_libs)

        if files.exists(SENTRY_HOME) is False:
           sudo("%s %s" % (self.virtualenv, SENTRY_HOME))        

        for lib in python_libs:
            sudo("%s/bin/pip install %s" % (SENTRY_HOME, lib))

        if files.exists("/home/web_log/sentry") is False:
            sudo("mkdir -p /home/web_log/sentry")

        sudo("%s/bin/sentry --config=/home/webapps/devops/sentry/sentry.conf.py upgrade" % SENTRY_HOME)
        
        #install supervisord
        with cd("/etc/init.d/"):
            if files.exists("supervisord-sentry") is False:
                sudo("ln -s /home/webapps/devops/sentry/supervisord-sentry")
                sudo("chkconfig supervisord-sentry on")

    

    def install_syslog_ng(cls):
    	sudo('yum install syslog-ng')
        sudo("cd /etc/syslog-ng/; mv syslog-ng.conf syslog-ng.conf.bak; ln -s /home/webapps/devops/syslog-ng/syslog-ng.conf")




class CrInstaller(object):

    """中证信用专用

    """

    @classmethod

    def default(cls):
        return cls()

    

    def __init__(self):
        self.douban_pip = "http://pypi.douban.com/simple/"
        self.python = "/usr/local/python27/bin/python"
        self.easy_install = "/usr/local/python27/bin/easy_install"
        self.virtualenv = "/usr/local/python27/bin/virtualenv"
        self.django14 = "/home/virtualenvs/py27"
        self.django14_pip = os.path.join(self.django14, "bin", "pip")
        self.django14_python = os.path.join(self.django14, "bin", "python")
        self.django18 = "/home/virtualenvs/dj18"
        self.django18_pip = os.path.join(self.django18, "bin", "pip")
        self.django18_python = os.path.join(self.django18, "bin", "python")
        self.web_log = "/home/web_log"

        self.system_libs = ["zlib-devel", 
            "pcre-devel", 
            "openssl-devel", 
            "bzip2-devel", 
            "curl", 
            "curl-devel", 
            "libjpeg-turbo-devel", 
            "freetype-devel", 
            "mysql", 
            "mysql-libs", 
            "mysql-devel", 
            "git", 
            "cyrus-sasl", 
            "cyrus-sasl-devel",
            "gcc",
            "gcc-c++",
            "gcc-gfortran",
            "nodejs",
            "npm",
            "bzip2",
            "xorg-x11-server-Xvfb",
            'libxslt-devel', 
            'libxml2-devel', 
            'libffi-devel',
            "lapack-devel",
            "blas-devel",
            "gcc-gfortran",
            "gcc",
            "gcc-c++",
            "atlas-devel", 
            "zip",
            "unzip",
            "numpy",
            "scipy",
            'psmisc',
        ]

        self.system_apps = set(["memcached", 
            "redis",
        ])

    

    def install_key(self):
        #install local public keys
        local("cp -f id_rsa ~/.ssh/")

        local("cat id_rsa.pub>~/.ssh/authorized_keys2")

        local("chmod -R 700 ~/.ssh")

        local("chmod 0600 ~/.ssh/id_rsa")

        #upload key files to remote

        put("id_rsa", "/tmp/")

        put("id_rsa.pub", "/tmp/")

        #change remote key files permission of myself and root

        run("if [ ! -d ~/.ssh ]; then\n cd && mkdir -p .ssh\n fi ")

        run("cp /tmp/id_rsa ~/.ssh/id_rsa")

        run("cat /tmp/id_rsa.pub > ~/.ssh/authorized_keys2")

        run("chmod -R 700 ~/.ssh")

        run("chmod 600 ~/.ssh/id_rsa")

        #for root

        sudo("if [ ! -d ~/.ssh ]; then\n cd /root && mkdir -p .ssh\n fi ")

        sudo("cp /tmp/id_rsa ~/.ssh/id_rsa")

        sudo("cat /tmp/id_rsa.pub > ~/.ssh/authorized_keys2")

        sudo("chmod -R 700 ~/.ssh")

        sudo("chmod 600 ~/.ssh/id_rsa")

        

    def install_env(self):

        """ run first

        """

        self.install_system_libs()
        self.install_system_apps()

        if files.exists(self.web_log) is False:
            sudo("mkdir %s" % self.web_log)

        self.install_python()

    def install_python(self):
        pytgz = "Python-2.7.6.tgz"

        if files.exists("/tmp/"+pytgz) is False:

            put(pytgz, "/tmp")

            

        if files.exists(self.python, True) is False:    

            sudo("cp /tmp/%s /root/" % pytgz)

            sudo("cd /root/ && tar -zxf Python-2.7.6.tgz && cd Python-2.7.6 && ./configure --prefix=/usr/local/python27 && make && make install")

        

        if files.exists(self.easy_install) is False:

            put("setuptools-3.3.zip", "/root", True)

            sudo("cd && unzip setuptools-3.3.zip && cd setuptools-3.3 && /usr/local/python27/bin/python setup.py install")

            sudo("%s virtualenv" % self.easy_install)

                   

    def install_system_libs(self):
        for lib in self.system_libs:
            sudo("yum install -y %s" % lib)

        sudo('yum groupinstall -y "X Window System"')
        sudo('yum groupinstall -y "Desktop"')
        sudo('yum groupinstall -y "Chinese Support"')
        sudo('yum install -y tigervnc-server')
        sudo('yum install -y firefox')

    def install_system_apps(self):
        for app in self.system_apps:
            sudo("yum install -y %s" % app)

    def install_phantomjs(self):
        sudo("npm install -g cnpm --registry=https://registry.npm.taobao.org")
        sudo("npm install -g phantomjs")    

    def install_sysctl(self):
        params = [
            "net.ipv4.tcp_max_tw_buckets=40000",
            "net.core.somaxconn=40000",
            "net.ipv4.tcp_tw_recycle=1",
            "net.ipv4.tcp_tw_reuse=1",
            "net.ipv4.tcp_fin_timeout=30",
        ]

        for param in params:
            sudo("sysctl %s" % param)
            param_name = param.split("=")[0]
            sudo("sed -i \"/%s/d\" /etc/sysctl.conf" % param_name)
            sudo("sed -i \"$ a %s\" /etc/sysctl.conf" % param)

    def install_django14(self):
        py_packages = set([
            "python-memcached", 
            "python-crontab", 
            "Markdown", 
            "south", 
            "six", 
            "raven", 
            "pillow", 
            "MySQL-python", 
            "requests", 
            "uwsgi", 
            "redis", 
            "threadpool", 
            'python-crontab',
            'raven',
            'beautifulsoup4',
            'selenium',
            'rq',
            "supervisor",
            "lxml",
            "html5lib",
            "numpy",
            #"scipy",
            #"pandas",
            #"scikit-learn",
            "django-smtp-ssl",
            "Django==1.4.22", 
            'jinja2',
        ])

        if files.exists(self.django14, True) is False:
            sudo("%s %s" % (self.virtualenv, self.django14))

        for pkg in py_packages:
            sudo("%s install %s" % (self.django14_pip ,pkg))

    def install_django18(self):
        py_packages = [
            "python-memcached", 
            "Markdown", 
            "raven", 
            "pillow",
            "MySQL-python", 
            "requests", 
            "uwsgi", 
            "redis", 
            "threadpool", 
            'python-crontab',
            'raven',
            'html5lib',
            'beautifulsoup4',
            'selenium',
            'rq',
            "supervisor",
            "django-smart-autoregister",
            "Cython",
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "Django==1.8.5",
            "gunicorn",
            "greenlet",
            "eventlet",
            "gevent",
            "django-smtp-ssl",
            'nltk',
            'jieba',
            'nose',
            'flake8',
            'jinja2',
        ]

        if files.exists(self.django18, True) is False:
            sudo("%s %s" % (self.virtualenv, self.django18))

        for pkg in py_packages:
            sudo("%s install -i %s --trusted-host pypi.douban.com %s" % (self.django18_pip, self.douban_pip, pkg))

        

    def install_haproxy(self):
        sudo("yum install -y haproxy")
        sudo("chkconfig haproxy on")
        sudo("cd /etc/haproxy && mv haproxy.cfg haproxy.cfg.bak && ln -s /home/webapps/devops/haproxy/haproxy_cr.cfg haproxy.cfg")
        sudo("service haproxy restart")

    def install_nginx(self):
        sudo("yum install -y nginx")
        sudo("chkconfig nginx on")
        sudo("cd /etc/nginx/ && mv nginx.conf nginx.conf.bak && ln -s /home/webapps/devops/nginx/nginx_cr.conf nginx.conf")
        sudo("service nginx restart")    

    def install_sentry(self):

    	SENTRY_HOME="/home/virtualenvs/sentry"

    	python_libs=["sentry", "supervisor", "raven", "MySQL-python", "redis", "python-memcached", "django-smtp-ssl"]

    	system_libs="bzip2 bzip2-devel"

        

        sudo("yum install -y %s" % system_libs)

        

        if files.exists(SENTRY_HOME) is False:

           sudo("%s %s" % (self.virtualenv, SENTRY_HOME))

        

        for lib in python_libs:

            sudo("%s/bin/pip install %s" % (SENTRY_HOME, lib))

        

        if files.exists("/home/web_log/sentry") is False:

            sudo("mkdir -p /home/web_log/sentry")

        

        sudo("%s/bin/sentry --config=/home/webapps/devops/sentry/sentry.conf.py upgrade" % SENTRY_HOME)

        #sudo("%s/bin/sentry --config=/home/webapps/devops/sentry/sentry.conf.py createsuperuser" % SENTRY_HOME)

        

        #install supervisord

        with cd("/etc/init.d/"):

            if files.exists("supervisord-sentry") is False:

                sudo("ln -s /home/webapps/devops/sentry/supervisord-sentry")

                sudo("chkconfig supervisord-sentry on")

    

    def install_syslog_ng(cls):

    	sudo('yum install syslog-ng')

        sudo("cd /etc/syslog-ng/; mv syslog-ng.conf syslog-ng.conf.bak; ln -s /home/webapps/devops/syslog-ng/syslog-ng.conf")

    

    def install_traffic_server(cls):

        #sudo("wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-1.noarch.rpm")

        #sudo("rpm -Uvh epel-release-7*.rpm")

        sudo("yum install trafficserver")

