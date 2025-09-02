#!/bin/bash

HOSTS="%(slaves_list)s master.local"

for host in ${HOSTS}; do
  echo === $host
  ssh $host -- $*;
done