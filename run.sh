#!/bin/bash
#
# bash script to test inventory.py
#
# 2017-08-14 Nereu

#DEBUG='-i'

#
# A list of servers, it will be inserted in database before the inventory
#
SERVERS="192.168.10.137 192.168.10.139 test"
SERVERS="192.168.10.137"

#
# inventory.py will connect in servers using SSH using the current user and keys,
# so you should test your connect wth the server before run this script.
# Using the list above as an example, you should issue a "ssh 192.169.10.138 uptime"
# to confirm that your SSH key is working.

mysql -vv <inventory.sql && \
for h in $(echo $SERVERS) ; do mysql -vv inventory -e "insert into host_list values ('${h}')" ; done && \
python ${DEBUG} inventory.py

