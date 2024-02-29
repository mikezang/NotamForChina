#!/bin/bash

mysql --user="root" --password="nsk20151228" --database="demo" --execute="use master;select database(), * from master.customer;select * from master.customer_order;use replica;select database();select * from replica.customer;select * from replica.customer_order; "

