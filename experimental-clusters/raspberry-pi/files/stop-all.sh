#!/bin/sh

#sudo su hadoop -c "/opt/hadoop/sbin/mr-jobhistory-daemon.sh stop historyserver"
sudo su hadoop -c "/opt/hadoop/sbin/stop-yarn.sh"
sudo su hadoop -c "/opt/hadoop/sbin/stop-dfs.sh"