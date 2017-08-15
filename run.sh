#!/bin/bash
#
# bash script to test inventory.py
#
# 2017-08-14 Nereu

SERVERS="py 192.168.10.138 test"

mysql -vv <inventory.sql && \
for h in $(echo $SERVERS) ; do mysql -vv inventory -e "insert into host_list values ('${h}')" ; done && \
python -i inventory.py

