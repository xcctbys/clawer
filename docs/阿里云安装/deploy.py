#coding=utf-8
""" auto deploy
usage: 
    fab -f deploy.py -i id_rsa.pub task

Get start:

"""

from fabric.api import run, sudo
from fabric.api import env
from fabric.api import roles
from fabric.api import local
from fabric.api import put
from fabric.api import cd

from software import Installer





class Server(object):
    SERVERS = [
        {"name":"", "public_ip":"", "internel_ip":"", "info":""},
        {"name":"web001", "public_ip":"123.56.24.180", "internel_ip":"10.0.3.2", "group":"hackdata"},
        {"name":"db001", "public_ip":"", "internel_ip":"10.0.3.2", "group":"hackdata"},
    ]

    def get_by_group(cls, name):
        pass


HOSTS = [
    "123.57.141.157",
    "123.57.22.110",
    "123.56.137.98", 
    "182.92.96.63",
    "47.88.138.142", #sg001
    "123.56.147.85",  #bj007 for risk 
    "101.200.135.196",  #bj008 for project p
    "182.92.198.146",  #bj009 
    "123.56.47.59", # bj010
    "123.57.70.221", # bj011
    "123.56.28.181", #vpc for test
]
    
env.roledefs = {
    'all': HOSTS,
    'home': [HOSTS[0], HOSTS[7]],
    'haproxy': [HOSTS[0], HOSTS[1], HOSTS[5], HOSTS[6], HOSTS[7], ],
    'nginx': [HOSTS[0], HOSTS[5], HOSTS[7], ],
    'syslog-ng': HOSTS,
    "sentry": [HOSTS[7]],
    "clawer": [HOSTS[0], HOSTS[1], HOSTS[2], HOSTS[4]],
    "clawer_web": [HOSTS[0]],
    "clawer_master": [HOSTS[0], ],
    "clawer_download": [HOSTS[1], HOSTS[2], HOSTS[4], ],
    "risk": [HOSTS[5], ],
    "p_beta": [HOSTS[6], ],
    "working": [HOSTS[0], HOSTS[7], ], 
    "working_master": [HOSTS[7], ], 
    "fico": [HOSTS[8], ],
    "vpc": [HOSTS[9], ],
}


installer = Installer.default()

    
    
@roles("haproxy")
def restart_haproxy():
    with cd("/home/webapps/devops/"):
        sudo("git pull")
        sudo("service haproxy check")
        sudo("service haproxy restart")
        
        
@roles("syslog-ng")
def restart_syslog_ng():
    with cd("/home/webapps/devops/"):
        sudo("git pull")
        sudo("service syslog-ng check")
        sudo("service syslog-ng restart")


@roles("nginx")
def restart_nginx():
    with cd("/home/webapps/devops/"):
        sudo("git pull")
        sudo("service nginx configtest")
        sudo("service nginx restart")



@roles("home")
def update_home():
    with cd("/home/webapps/princetechs"):
        sudo("git pull")


###################
# clawer
###################


@roles("clawer")
def clawer_update():
    with cd("/home/webapps/nice-clawer/confs/production"):
        sudo("git pull")
        sudo("chown -R nginx:nginx /home/web_log/nice-clawer")



@roles("clawer_web")
def clawer_web_restart():
    with cd("/home/webapps/nice-clawer/confs/production"):
        sudo("git pull")
        sudo("chown -R nginx:nginx /home/web_log/nice-clawer")
        sudo("./uwsgi-clawer.sh restart")


@roles("clawer_download")
def clawer_worker_reload():
    with cd("/home/webapps/nice-clawer/confs/production"):
        sudo("git pull")
        sudo("/etc/init.d/supervisord reload")


@roles("clawer_download")
def clawer_worker_restart():
    with cd("/home/webapps/nice-clawer/confs/production"):
        sudo("git pull")
        sudo("/etc/init.d/supervisord restart")


@roles("clawer_master")
def clawer_migrate():
    with cd("/home/webapps/nice-clawer/confs/production"):
        sudo("git pull")
        sudo("./bg_cmd.sh migrate clawer")
        sudo("./bg_cmd.sh migrate captcha")
        sudo("./bg_cmd.sh migrate enterprise")


##########################
# end clawer
##########################



###################
# risk
###################

@roles("risk")
def risk_update():
    with cd("/home/webapps/risk/confs/production"):
        sudo("git pull")
        sudo("chmod -R 0775 /home/web_log/risk")
        sudo("service supervisord reload")
        

@roles("risk")
def risk_migrate():
    with cd("/home/webapps/risk/confs/production"):
        sudo("git pull")
        sudo("./bg_cmd.sh migrate")


@roles("risk")
def risk_start():
    with cd("/home/webapps/risk/confs/production"):
        sudo("chmod -R 0775 /home/web_log/risk")
        sudo("service supervisord start")


@roles("risk")
def risk_stop():
    with cd("/home/webapps/risk/confs/production"):
        sudo("chmod -R 0775 /home/web_log/risk")
        sudo("service supervisord stop")

###################
# end risk
###################






###################
# working
###################

WORKDING_DIR = "/home/webapps/hr/webapp/confs/production"

@roles("working")
def working_update():
    with cd(WORKDING_DIR):
        sudo("git pull")
        sudo("chown -R nginx:nginx /home/web_log/working.debug.log")
        
@roles("working_master")
def working_reload():
    with cd(WORKDING_DIR):
        sudo("git pull")
        sudo("chown -R nginx:nginx /home/web_log/working.debug.log")
        sudo("service supervisord reload")


@roles("working_master")
def working_migrate():
    with cd(WORKDING_DIR):
        sudo("git pull")
        sudo("./bg_cmd.sh migrate")


@roles("working_master")
def working_start():
    with cd(WORKDING_DIR):
        sudo("git pull")
        sudo("chown -R nginx:nginx /home/web_log/working.debug.log")
        sudo("service supervisord start")


@roles("working_master")
def working_stop():
    with cd(WORKDING_DIR):
        sudo("service supervisord stop")

@roles("working_master")
def working_restart():
    with cd(WORKDING_DIR):
        sudo("git pull")
        sudo("service supervisord stop")
        sudo("service supervisord start")


##################
# end working
###################





###################
# project p
###################

@roles("p_beta")
def p_beta_update():
    with cd('/home/webapps/p'):
        sudo("git checkout dev")

    with cd("/home/webapps/p/confs/beta"):
        sudo("git pull")
        sudo("git checkout dev")
        sudo("chown -R nginx:nginx /home/web_log/p")
        sudo("chmod -R 0775 /home/web_log/p")
        sudo("service supervisord reload")
        

@roles("p_beta")
def p_beta_migrate():
    with cd('/home/webapps/p'):
        sudo("git checkout dev")

    with cd("/home/webapps/p/confs/beta"):
        sudo("git pull")
        sudo("./bg_cmd.sh migrate")


@roles("p_beta")
def p_beta_restart():
    with cd("/home/webapps/p/confs/beta"):
        sudo("chmod -R 0775 /home/web_log/p")
        sudo("service supervisord restart")

@roles("p_beta")
def p_beta_stop():
    with cd("/home/webapps/p/confs/beta"):
        sudo("chmod -R 0775 /home/web_log/p")
        sudo("service supervisord stop")


@roles("p_beta")
def p_beta_start():
    with cd("/home/webapps/p/confs/beta"):
        sudo("chmod -R 0775 /home/web_log/p")
        sudo("service supervisord start")


@roles("p_beta")
def p_beta_install_requirements():
    with cd("/home/webapps/p/confs/beta"):
        sudo("git pull")
        sudo("/home/virtualenvs/dj18/bin/pip install -r /home/webapps/p/requirements.txt")

###################
# end project p
###################



###################
# fico863
###################

FICO_WORKDIR = "/home/webapps/fico863/confs/production"
FICO_LOG = "/home/web_log/fico863"

@roles("fico")
def fico_update():
    with cd(FICO_WORKDIR):
        sudo("git pull")
        sudo("chown -R nginx:nginx %s" % FICO_LOG)
        sudo("service supervisord reload")
        

@roles("fico")
def fico_migrate():
    with cd(FICO_WORKDIR):
        sudo("git pull")
        sudo("./bg_cmd.sh migrate")


@roles("fico")
def fico_restart():
    with cd(FICO_WORKDIR):
        sudo("chown -R nginx:nginx %s" % FICO_LOG)
        sudo("service supervisord restart")


###################
# end fico863
###################


# install system environment
def install_key():
    installer.install_key()
    

def sysctl():
    installer.install_sysctl()
    

################
# sentry
################
def install_sentry():
    installer.install_sentry()


@roles("sentry")
def restart_sentry():
    with cd("/home/webapps/devops/sentry"):
        sudo("git pull")
        sudo("/etc/init.d/supervisord-sentry stop")
        sudo("/etc/init.d/supervisord-sentry start")


################
# end sentry
################

def install_env():
    installer.install_env()
    
    
def install_phantomjs():
    installer.install_phantomjs()
    
    
def install_django14():
    installer.install_django14()
    
    
def install_django18():
    installer.install_django18()
    

def install_nginx():
    installer.install_nginx()
    

def install_haproxy():
    installer.install_haproxy()
    
    
def install_syslog_ng():
    installer.install_syslog_ng()
