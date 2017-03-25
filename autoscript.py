#!/usr/bin/python2.7

import boto
import sys
import time
import boto.ec2.cloudwatch
from datetime import datetime, timedelta
import os
import subprocess
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from os.path import basename
import glob

newpath = r'/tmp/reports-mysql'
if not os.path.exists(newpath):
    os.makedirs(newpath)

rds_instance_dict = dict()

rds_instance_dict = {
    'rds instance name': {
        'threshold': 50,
        'email-reports': '',
        'endpoint': '',
        'password': '',
        'username': '',
        'database': '',
        'slave': 'no',
        }}


cw = boto.ec2.cloudwatch.connect_to_region('ap-southeast-1')
path = '/scripts/REPORTS'
for rds_instance in rds_instance_dict.keys():
    try:
        files = glob.glob('/tmp/reports-mysql/*.txt')
        for f in files:
                os.remove(f)        

        rds_metric = cw.get_metric_statistics(
                300,
                datetime.utcnow() - timedelta(seconds=600),
                datetime.utcnow(),
                'CPUUtilization',
                'AWS/RDS',
                'Maximum',
                dimensions={'DBInstanceIdentifier': rds_instance}
                )
        if rds_metric[0]['Maximum'] >= rds_instance_dict[rds_instance]["threshold"]:
		if rds_instance_dict[rds_instance]["slave"] == 'yes':
	    	      os.system("python "+path+"/mysql-slave.py -e "+rds_instance_dict[rds_instance]["endpoint"]+" -d "+rds_instance_dict[rds_instance]["database"]+" -u "+rds_instance_dict[rds_instance]["username"]+" -p'"+rds_instance_dict[rds_instance]["password"]+"'")
	        else:
	    	      os.system("python "+path+"/mysql.py -e "+rds_instance_dict[rds_instance]["endpoint"]+" -d "+rds_instance_dict[rds_instance]["database"]+" -u "+rds_instance_dict[rds_instance]["username"]+" -p'"+rds_instance_dict[rds_instance]["password"]+"'")
	        os.system("bash "+path+"/mysql-auto-diagnosis.sh "+rds_instance)
	        user = 'ses user access key'
	    	pw   = 'ses user secret acess key'
	    	host = 'email-smtp.us-east-1.amazonaws.com'
	    	port = 465
 	     	fromaddr = ""
	    	toaddr = rds_instance_dict[rds_instance]["email-reports"]
	    	msg = MIMEMultipart()
	    	msg['From'] = fromaddr
   	    	msg['To'] = toaddr
 	    	msg['Subject'] = "DevOps auto generated diagnosis report for "+rds_instance+" with CPU Utilization "+ str(rds_metric[0]['Maximum'])

	    	body = "Please find the attached mysql-report for "+rds_instance+" it crossed the CPU Utilization threshold "+ str(rds_instance_dict[rds_instance]["threshold"])
	    	msg.attach(MIMEText(body, 'plain'))

	    	filenames = ("/tmp/reports-mysql/"+rds_instance+".diagnosis.txt","/tmp/reports-mysql/"+rds_instance+"-detailed-devops-report.txt")
#	    	print filenames
	    	for filename in filenames:
         		attachment = open(filename, "rb")
        		part = MIMEBase('application', 'octet-stream')
       			part.set_payload((attachment).read())
        		encoders.encode_base64(part)
        		part.add_header('Content-Disposition', "attachment; filename= %s" % basename(filename))
        		msg.attach(part)

	    	server = smtplib.SMTP_SSL(host, port, '')
	    	server.set_debuglevel(1)
	    	server.login(user, pw)
	    	text = msg.as_string()
	    	server.sendmail(fromaddr, toaddr, text)
	    	server.quit()
        else:
	    print "current CPU Utilization value of "+rds_instance+" is "+ str(rds_metric[0]['Maximum'])+"  it did not breach the threshold of "+ str(rds_instance_dict[rds_instance]["threshold"])
    except Exception as exp:
       print "Exception ",exp,"occured while running for rds instance",rds_instance

