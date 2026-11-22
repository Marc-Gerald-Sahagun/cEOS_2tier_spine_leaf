#!/bin/bash


for n in server1 server2 server3 server4; do echo $n; docker exec $n ip addr show | grep bond0 | grep inet;done
