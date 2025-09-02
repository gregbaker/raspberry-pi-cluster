# Cluster Setup and Configuration

The steps here should get a cluster up configured.

## Raspbian Setup

You'll need to hook up to a monitor and keyboard/mouse on one node just to get Raspbian set up so you can connect remotely in the future.

[Download Raspbian Lite](https://www.raspberrypi.org/downloads/) and transfer the image to your SD Card. Like this:

```
sudo dd bs=4M if=2017-08-16-raspbian-stretch-lite.img of=/dev/sdX
```

Put the SD in the Pi and start it up. Log in with the default username and password (pi:raspberry). Open the config tool ```sudo raspi-config``` and at the setup menu:

* Enable SSH.
* Enlarge the disk (although this could be done later on each node if you have heterogeneous storage).
* Change the memory split to minimize video RAM (16M).
* Overclock the processor if you like (although I didn't).

From here on, you should be able to connect remotely and disconnect the display and keyboard. Make sure you can connect:

```
ssh pi@raspberrypi.local
```

You can now start working with Fabric to set up some one-time things. This task distributes your SSH public key (```~/.ssh/id_rsa.pub```) to the cluster, and create keys for the pi@ user.

```
fab -H pi@raspberrypi.local auth_config
```

This removes many packages, so there is as much free disk space (and as few processes running) as possible:

```
fab -H pi@raspberrypi.local clean_raspbian
```

Shut down the Pi. The SD card now has the master image you can use to start each node. Take a snapshot:

```
sudo dd bs=4M if=/dev/sdX of=basic_setup.img
```

This task fetches a bunch of files (to your local computer) that you'll need later for the install:

```
fab -H pi@raspberrypi.local fetch_files
```

## For Each Node

Copy the master disk image to this node's SD card. (Not necessary for SD card you used to create the image, since it's already in this state):

```
sudo dd bs=4M if=basic_setup.img of=/dev/sdX
```

Format the USB drive that will store the Hadoop data on this node:

```
sudo mkfs.ext4 -L HADOOP /dev/sdY1
```

Insert the SD card, USB drive, and start up the node. Set its hostname to be distinct. Nodes should be called ```master``` and ```hadoop1```, ```hadoop2```, ```hadoop3```, ...

```
fab -H pi@raspberrypi.local --set=hostname=hadoopX set_hostname
```

## Hadoop Installation


In ```fabfile.py```, set ```SLAVES``` so you have the right number of nodes: the default setup is one master and six slaves. Get some basic configuration done for each node:

```
fab node_config
```

With **all nodes running**, get the SSH signatures distributed to each node, so there's no "authenticity of host can't be established" problems later:

```
fab ssh_keyscan
```

Install Hadoop and Spark:

```
fab install_hadoop
fab install_spark
```

If you'd like to change the password for the pi@ accounts:

```
fab --set=passwd="secretpassword" change_password
```


From here, the cluster should be good to go. (You may need to reboot or do an ```ntpdate``` on each node to get the clocks right.)


## Running The Cluster

Before you start the Hadoop tools for the first time, the HDFS must be formatted. SSH to the master node (```ssh pi@master.local```) and:

```
dfs-format
```

Then to start YARN and HDFS:

```
start-all
```

To submit jobs with either YARN or Spark:

```
yarn jar wordcount.jar WordCount /user/pi/inputs /user/pi/output
spark-submit --master yarn --deploy-mode cluster wordcount.py /user/pi/wordcount /user/pi/output
```

To shut everything down:

```
stop-all # stop Hadoop
halt-all # shutdown the nodes
```


