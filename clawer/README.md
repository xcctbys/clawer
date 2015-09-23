# Prequired

- Django 1.4.x
- Redis
- Memcached
- Celery


# Create Database on MySQL

       CREATE DATABASE `clawer` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
      
       #create user
       CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'localhost';
      
       CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'%';
       
       
# Crontab
      #for root
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_generator_test
      
      #for nginx user
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis_merge
      
      #############################
      # topologic #
      
      #master
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_generator_test
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_dispatch
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis_merge
      
      
      #slave
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis --process=2 --run=290
      
      ## start download worker
      # mkdir /home/web_log/nice-clawer
      # chown -R nginx:nginx /home/web_log/nice-clawer
      # mkdir /data/clawer
      # chown -R nginx:nginx /data/clawer
      
      */5 * * * * DJANGO_SETTINGS_MODULE=settings_pro /home/virtualenvs/py27/bin/rqworker --url redis://10.171.34.147/0  -v --pid /tmp/rq_worker1.pid --burst -P /home/webapps/nice-clawer/clawer/ task_downloader 
      
     
# Supervisor for Clawer worker

      ## start download worker
      # mkdir /home/web_log/nice-clawer
      # chown -R nginx:nginx /home/web_log/nice-clawer
      # mkdir /data/clawer
      # chown -R nginx:nginx /data/clawer
      # mkdir /data/media
      # chown -R nginx:nginx /data/media
      
      /home/virtualenvs/py27/bin/supervisord -c /home/webapps/nice-clawer/confs/production/supervisor.ini
