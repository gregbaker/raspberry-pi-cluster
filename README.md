# Raspberry Pi Hadoop Cluster

Have you always wanted your very own fantastically-slow compute cluster? Then you have come to the right place.

This code will automatically (or as automatically as possible) configure a collection of [Raspberry Pis](https://www.raspberrypi.org/) as a [Hadoop](https://hadoop.apache.org/) cluster.

## Instructions

In this repo, you'll find a [parts list](PARTS.md) and [setup instructions](SETUP.md).

As for using the cluster to do things, I'll defer to my [assignment that uses the cluster](https://courses.cs.sfu.ca/2015fa-cmpt-732-g1/pages/Assignment5A) for details.

The setup I used is almost exactly the same as [Nigel Pond's Raspberry Pi cluster](http://www.nigelpond.com/2015/06/27/how-to-build-a-7-node-raspberry-pi-cluster/). As I was planning, I kept deciding to do things differently, but then circling back and doing exactly the same thing he did (including buying the same case, which I didn't realize until I clicked back just now). Many thanks to him for the inspiration!


## Why?

Why not?

In my case, as a teaching tool: it's all well and good to read in the docs that HDFS and YARN will heal themselves if a node fails. It's another to see it actually happen. When I learned that the ops staff were not thrilled about the "go into the server room and unplug things" approach, a collection of Pis was the answer.

With everything nice and tidy in Fabric, I can fix any configuration problems that arise with abuse of the cluster.

## TODO

Since the USB drive gets better read-write speed than the SD card, I would like to try moving the Hadoop installation there.

It might be nice to have a SquashFS filesystem for the basic installation, and a AuFS/UnionFS for everything on top of that. That would make re-imaging the nodes super easy.
