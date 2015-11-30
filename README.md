# Prequired

- Django 1.4.x
- Redis
- Memcached
- RQ


# Create Database on MySQL

       CREATE DATABASE `clawer` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
      
       #create user
       CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'localhost';
      
       CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'%';
       
       
# Crontab
      
      #############################
      # topologic #
      
      # master
      ## for root
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_generator_install
      ## for nginx user
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_dispatch
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis_merge
      
      
      #slave
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./bg_cmd.sh task_analysis --thread=2 --run=290
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/production;./shrink_tmp.sh
      
      #foreign slave
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./foreign_bg_cmd.sh task_analysis --thread=2 --run=290
      ## must run with root
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/production;./foreign_bg_cmd.sh task_generator_install --foreign
      
     
# Supervisor for Clawer worker

Run in China

      ## start download worker
      # mkdir /home/web_log/nice-clawer
      # chown -R nginx:nginx /home/web_log/nice-clawer
      # mkdir /data/clawer
      # chown -R nginx:nginx /data/clawer
      # mkdir /data/media
      # chown -R nginx:nginx /data/media
      
      ln -s /home/webapps/nice-clawer/confs/production/supervisord
      chkconfig supervisord on
      service supervisord restart
      

Run out China

      ln -s /home/webapps/nice-clawer/confs/production/supervisord
      ln -s /home/webapps/nice-clawer/confs/production/supervisor-foreign.ini supervisor.ini
      chkconfig supervisord on
      service supervisord restart
      
      
      
      


