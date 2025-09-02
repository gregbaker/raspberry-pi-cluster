#!/bin/sh

sudo su hadoop -c "/opt/hadoop/sbin/start-dfs.sh"
sudo su hadoop -c "/opt/hadoop/sbin/start-yarn.sh"
#sudo su hadoop -c "/opt/hadoop/sbin/mr-jobhistory-daemon.sh start historyserver"
