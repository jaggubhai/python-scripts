#!/usr/bin/python2.7

import boto
import sys
import time
from boto import ec2
import boto.ec2.cloudwatch
import datetime
from boto.sns import connect_to_region
from pprint import pprint
connection=ec2.connect_to_region("ap-southeast-1")
reservations=connection.get_all_instances();

instance_id_map = dict()

for reservation in reservations:
 for instances in reservation.instances:
    #print dir(instances)   #for debugging
 	#print instances.tags['Name'], instances.tags['pod'], instances.id #for debugging
    if instances.tags['env'] == "prod" and instances.state == "running":
        instance_id_map[str(instances.id)] = dict()
        instance_id_map[str(instances.id)]['Name'] = instances.tags['Name']
        instance_id_map[str(instances.id)]['pod'] = instances.tags['pod']

sns = connect_to_region('ap-southeast-1')
topics = sns.get_all_topics()

c = boto.ec2.cloudwatch.connect_to_region('ap-southeast-1')
mylist=instance_id_map.keys()
#print len(mylist) #for debugging

for items in mylist:

    if True:
        topic = 'topicname'
        alarm_name = str(instance_id_map[items]['Name']) + "-CPUUtilization-" + str(instance_id_map[items]['pod']) + "-Critical"
        print items,instance_id_map[items]['Name']
        print c.list_metrics(dimensions={'InstanceId':[items]},
                         metric_name="CPUUtilization")
        metric = c.list_metrics(dimensions={'InstanceId':[items]},
                         metric_name="CPUUtilization")[0]
        metric.create_alarm(name=alarm_name, comparison='>=', threshold=75, period=300,
                    evaluation_periods=1, statistic='Maximum', alarm_actions=[topic])
        time.sleep(2)
