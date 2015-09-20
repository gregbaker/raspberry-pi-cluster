export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export HADOOP_HOME=%(hadoop_home)s
export PATH=/home/pi/bin:/opt/hadoop/bin:/opt/hbase/bin:/opt/spark/bin:$PATH

export HADOOP_PREFIX=${HADOOP_HOME}
export HADOOP_INSTALL=${HADOOP_HOME}
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop