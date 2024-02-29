#!/bin/sh

ssh-keygen -t rsa -f $1

cat ~/.ssh/id_rsa.pub | ssh mobile@$2 "cat - >> ~/.ssh/authorized_keys"
