#!/bin/bash

COUNT=99999
OUT=test.html


echo "start at `date '+%Y-%m-%d %H:%M:%S'`"

for (( i=0; i<${COUNT}; i++))
do
    curl 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?entId=a1a1a1a021ced5020121e19fc345143e&credit_ticket=23E3B6AFB92BA8FB3C9B33FA08F973D6&entNo=110102012003809&timeStamp=1445312300861' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml' -H 'Cookie: JSESSIONID=GgTpWlvb624kKV0yc9s2WWTF8wDyDJNh1KJR5vv2PsdL6yjMjMsc!1602704003; BIGipServerpool_xy3_web=1075161280.17183.0000' -H 'Connection: keep-alive' --compressed -o ${OUT}
    
    search=`grep 110102012003809 ${OUT}`
    if test -n "${search}"
    then
         echo "search result is ${search}"
         echo "download is `date '+%Y-%m-%d %H:%M:%S'`"
    else
         echo "failed"
         break
    fi

    sleep 30

done

echo "end at `date '+%Y-%m-%d %H:%M:%S'`"
