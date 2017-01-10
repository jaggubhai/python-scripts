#!/usr/bin/python2.7

# this python script using boto prints out the ec2 instances with their private IP addresses. 

import boto
import sys
from boto import ec2
connection=ec2.connect_to_region("ap-southeast-1")
reservations=connection.get_all_instances();

for reservation in reservations:
 for instances in reservation.instances:
        print "%s \t \t %s" % (instances.tags['Name'], instances.private_ip_address)
