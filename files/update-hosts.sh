#!/bin/bash

# Put my own hostname in /etc/hosts so it can be found by hbase/zookeeper
# https://mail-archives.apache.org/mod_mbox/hbase-user/200912.mbox/%3C1260256530.30509.49.camel@pyro.bengueladev.com%3E

IPADDR=$(ifconfig eth0 | grep -Po '(?<=inet addr:)\S+')
HOSTNAME=$(hostname).local

cat /etc/hosts.template | sed "s/HOST/$IPADDR $HOSTNAME/" > /etc/hosts