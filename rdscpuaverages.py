#!/usr/bin/python2.7

import boto
import sys
import time
import boto.ec2.cloudwatch
from datetime import datetime, timedelta
import os
import subprocess
import smtplib
from prettytable import PrettyTable
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from boto import rds
from hurry.filesize import size
from os.path import basename
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", dest="time", help="Give the time threshold")
args = parser.parse_args()

cw = boto.ec2.cloudwatch.connect_to_region('ap-southeast-1')
rds_conn = rds.connect_to_region('ap-southeast-1')
dbinstances = rds_conn.get_all_dbinstances()

present_time = datetime.utcnow()
five_days_back = datetime.utcnow() - timedelta(days=5)
ten_days_back = datetime.utcnow() - timedelta(days=10)
fourteen_days_back = datetime.utcnow() - timedelta(days=14)

time_list = [(present_time, five_days_back), (five_days_back, ten_days_back), (ten_days_back, fourteen_days_back)]
Avg_threshold = int(args.time)

tbl = PrettyTable(["Name", "Inst.type", "Max_CPU", "Max_Connections", "Min_FreeableMemory", "Billed hours"])
tbl.padding_width=1

newpath = r'/tmp/reports-rds'
if not os.path.exists(newpath):
    os.makedirs(newpath)

def get_metrics(start_time, end_time, dbi_id, namespace, metrics_type, period):
    cpu_metrics = cw.get_metric_statistics(
         period,
         end_time,
         start_time,
         namespace,
         'AWS/RDS',
         metrics_type,
         dimensions={'DBInstanceIdentifier': dbinstance.id}
         )
    return cpu_metrics

fo = open("/tmp/reports-rds/rdsinstancescpureport.txt", "wb")
for dbinstance in dbinstances:
    maximum_cpu_value = 0
    maximum_conn_value = 0
    minimum_freeable_memory = 1000000000000
    billed_hours = len(get_metrics(present_time, fourteen_days_back, dbinstance.id,'CPUUtilization', 'Minimum', 3600))
    if dbinstance.status == "available":
        print "===================================================================================================="
        for (start_time, end_time) in time_list:
            max_metrics = get_metrics(start_time, end_time, dbinstance.id, 'CPUUtilization', 'Maximum', 300)
            conn_metrics = get_metrics(start_time, end_time, dbinstance.id, 'DatabaseConnections', 'Maximum', 300)
            freeable_memory_metrics = get_metrics(start_time, end_time, dbinstance.id, 'FreeableMemory', 'Minimum', 300)
            if not max_metrics and conn_metrics:
                if maximum_conn_value < sorted(conn_metrics , key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']:
                    maximum_conn_value = sorted(conn_metrics , key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']
                continue
            elif not max_metrics and not conn_metrics:
                continue
            if minimum_freeable_memory > sorted(freeable_memory_metrics, key= lambda r: r['Minimum'])[0]['Minimum']:
                minimum_freeable_memory = sorted(freeable_memory_metrics, key= lambda r: r['Minimum'])[0]['Minimum']
            if maximum_cpu_value < sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']:
                maximum_cpu_value = sorted(max_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']
            if maximum_conn_value < sorted(conn_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']:
                maximum_conn_value = sorted(conn_metrics, key= lambda r: r['Maximum'], reverse=True)[0]['Maximum']
            if maximum_cpu_value <= Avg_threshold and end_time != fourteen_days_back:
                continue
            elif maximum_cpu_value <= Avg_threshold and end_time == fourteen_days_back:
                tbl.add_row([dbinstance.id, dbinstance.instance_class, maximum_cpu_value, maximum_conn_value, size(minimum_freeable_memory), billed_hours])
            elif maximum_cpu_value > Avg_threshold:
                print dbinstance.id, start_time, end_time, len(max_metrics), maximum_cpu_value, maximum_conn_value, size(minimum_freeable_memory), billed_hours
                break

# print tbl.get_string(sortby="Name")
fo.write(tbl.get_string(sortby="Name"))
fo.close()

user = 'SES USER ACCESS KEY'
pw   = 'SES USER SECRET ACCESS KEY'
host = 'email-smtp.us-east-1.amazonaws.com'
port = 465
fromaddr = "FROM_ADDRESS"
toaddr = "TO_ADDRESS"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "rds isntances DevOps detailed report"

body = "Please find the attached rdsinstances-report text file"
msg.attach(MIMEText(body, 'plain'))

filename = "rdsinstancescpureport.txt"
attachment = open("/tmp/reports-rds/rdsinstancescpureport.txt", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % basename(filename))
msg.attach(part)

server = smtplib.SMTP_SSL(host, port, 'swiggy.com')
server.set_debuglevel(1)
server.login(user, pw)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
