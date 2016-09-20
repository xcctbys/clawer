#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from fabric.api import env, cd, run, parallel
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append


env.user = "root"
# env.password = "plkjPlkjdacheng!"
env.password = "haijunt0044"
env.hosts = [
    # "139.217.8.138",
    # "139.217.14.223",
    # "139.217.10.84",
    "47.88.148.27"
]
LOCAL_PROJECT_PATH = "~/Projects/nice-clawer"
REMOTE_PROJECT_PATH = "/home/webapps"


@parallel
def install():
    # _create_used_folders()
    _rsync_project()
    # _install_project_deps()


@parallel
def ssh_key(key_file="~/.ssh/id_rsa.pub"):
    key_text = _read_ssh_pub_key(key_file)
    run("[ -d ~/.ssh ] || mkdir -p ~/.ssh")
    append('~/.ssh/authorized_keys', key_text)


def _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH):
    run("yum install -y rsync")
    rsync_project(local_dir=local_project_path,
                  remote_dir=remote_project_path,
                  exclude=".git")


def _create_used_folders():
    # Create project folder
    run("mkdir -p {0}".format(REMOTE_PROJECT_PATH))
    run("mkdir -p /home/web_log")
    run("mkdir -p /home/web_log/nice-clawer")


def _install_project_deps():

    # run("yum install -y epel-release")
    # run("yum update -y")
    # run("yum install -y PyQt4*")
    # Install all projects deps, such as python-devel, mysql-devel and pip, setuptools ...
    # run("yum install -y wget python-devel python-pip mariadb mysql-devel \
    #     gcc gcc-c++ cmake blas-devel lapack-devel libxml2 libxml2-devel \
    #     libxslt libxslt-devel libjpeg-devel zlib-devel xorg-x11-server-Xvfb \
    #     mysql-connector-python")
    PIP = "pip install --upgrade --no-index -f pypi"
    with cd("{0}/nice-clawer/deploy".format(REMOTE_PROJECT_PATH)):
        run("{0} pip setuptools".format(PIP))
        run("{0} -r {1}".format(PIP, "../clawer/requirements.txt"))


def _read_ssh_pub_key(key_file):
    key_file = os.path.expanduser(key_file)
    # Check is it a pub key.
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()
