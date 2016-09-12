STAGING=~/hdfs-staging
DEST=/user/pi

wordcount:
	mkdir -p ${STAGING}
	rm -rf ${STAGING}/gutenberg ${STAGING}/wordcount
	-wget -nc http://www.nltk.org/nltk_data/packages/corpora/gutenberg.zip -O /tmp/gutenberg.zip
	unzip /tmp/gutenberg.zip -d ${STAGING}
	mv ${STAGING}/gutenberg ${STAGING}/wordcount
	rm ${STAGING}/wordcount/README

euler:
	rm -rf ${STAGING}/euler-input
	mkdir -p ${STAGING}/euler-input
	for i in `seq 1 100`; do echo 10000000 >> ${STAGING}/euler-input/input-$$i.txt; done

big-file:
	hdfs dfs -mkdir -p ${DEST}
	[ -f /tmp/bigfile ] || tar -ckf /tmp/bigfile /usr/lib
	hdfs dfs -D dfs.replication=4 -copyFromLocal /tmp/bigfile ${DEST}/big-file-1
	hdfs dfs -D dfs.replication=4 -cp ${DEST}/big-file-1 ${DEST}/big-file-2

hdfs-files: wordcount euler
	hdfs dfs -mkdir -p ${DEST}
	-hdfs dfs -rm -r ${DEST}/wordcount ${DEST}/euler-input
	hdfs dfs -copyFromLocal ${STAGING}/wordcount ${STAGING}/euler-input ${DEST}
