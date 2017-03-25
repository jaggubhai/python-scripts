#!/usr/bin/python2.7

import boto
import sys
import time
import os
from boto import ec2
import boto.ec2.cloudwatch
from datetime import datetime, timedelta
from boto.ec2 import cloudwatch
from prettytable import PrettyTable
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from os.path import basename
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", dest="time", help="Give the time threshold")
args = parser.parse_args()

connection=ec2.connect_to_region("ap-southeast-1")
reservations=connection.get_all_instances();
cw = cloudwatch.connect_to_region('ap-southeast-1')

present_time = datetime.utcnow()
five_days_back = datetime.utcnow() - timedelta(days=5)
ten_days_back = datetime.utcnow() - timedelta(days=10)
fourteen_days_back = datetime.utcnow() - timedelta(days=14)

time_list = [(present_time, five_days_back), (five_days_back, ten_days_back), (ten_days_back, fourteen_days_back)]
Avg_threshold = int(args.time)

tbl = PrettyTable(["Name", "env", "Inst.iD", "POD", "Inst.type", "Average", "Maximum", "Billed hours"])
tbl.padding_width=1

newpath = r'/tmp/reports-ec2'
if not os.path.exists(newpath):
    os.makedirs(newpath)

def get_metrics(start_time, end_time, instance_id, metrics_type, period):
    cpu_metrics = cw.get_metric_statistics(
         period,
         end_time,
         start_time,
         'CPUUtilization',
         'AWS/EC2',
         metrics_type,
         dimensions={'InstanceId': instance_id}
         )
    return cpu_metrics
fo = open("/tmp/reports-ec2/ec2instancescpureport.txt", "wb")
for reservation in reservations:
    for instance in reservation.instances:
        maximum_cpu_value = 0
        maximum_avg_value = 0
        billed_hours = len(get_metrics(present_time, fourteen_days_back, instance.id, 'Average', 3600))
        if instance.state != "running":
            print "===================================================================================================="
            print "Instance", instance.tags['Name'], "is not running"
            continue
        else:
            print "===================================================================================================="
            print 'Name', "start_time", "end_time", "len(avg_metrics)", "len(max_metrics)", "maximum_avg_value", "maximum_cpu_value", "billed_hours"
            for (start_time, end_time) in time_list:
                avg_metrics = get_metrics(start_time, end_time, instance.id,'Average', 300)
                max_metrics = get_metrics(start_time, end_time, instance.id,'Maximum', 300)
                print instance.tags['Name'], start_time, end_time, len(avg_metrics), len(max_metrics), maximum_avg_value, maximum_cpu_value, billed_hours
                if not avg_metrics and max_metrics:
                    if maximum_cpu_value < sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']:
                        maximum_cpu_value = sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']
                    continue
                elif not avg_metrics and not max_metrics:
                    continue
                if maximum_avg_value < sorted(avg_metrics, key= lambda r: r['Average'], reverse=True)[0]['Average']:
                    maximum_avg_value = sorted(avg_metrics, key= lambda r: r['Average'], reverse=True)[0]['Average']
                if maximum_cpu_value < sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']:
                    maximum_cpu_value = sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']
                if maximum_avg_value <= Avg_threshold and end_time != fourteen_days_back:
                    continue
                elif maximum_avg_value <= Avg_threshold and end_time == fourteen_days_back:
                    tbl.add_row([instance.tags['Name'], instance.tags['env'], instance.id, instance.tags['pod'], instance.instance_type, maximum_avg_value, maximum_cpu_value, billed_hours])
                elif maximum_avg_value > Avg_threshold:
                    print "MAX AVG greater than ", Avg_threshold, " ", instance.tags['Name'], start_time, end_time, len(avg_metrics), len(max_metrics), maximum_avg_value, maximum_cpu_value, billed_hours
                    break
# print tbl

fo.write(tbl.get_string(sortby="POD"))
fo.close()

user = 'SES USER ACCESS KEYS'
pw   = 'SES USER SECRET ACCESS KEY'
host = 'email-smtp.us-east-1.amazonaws.com'
port = 465
fromaddr = "FROM_ADDRESS"
toaddr = "TO_ADDRESS"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "EC2 isntances DevOps detailed report"

body = "Please find the attached ec2instances-report text file"
msg.attach(MIMEText(body, 'plain'))

filename = "ec2instancescpureport.txt"
attachment = open("/tmp/reports-ec2/ec2instancescpureport.txt", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % basename(filename))
msg.attach(part)

server = smtplib.SMTP_SSL(host, port, '******.com')
server.set_debuglevel(1)
server.login(user, pw)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
