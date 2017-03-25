#!/usr/bin/python2.7

import mysql.connector
from mysql.connector import Error
import argparse
import subprocess
import boto
from boto import ec2
import collections
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from prettytable import PrettyTable

parser = argparse.ArgumentParser()
parser.add_argument("-e", dest="host", help="Give the RDS instance endpoint")
parser.add_argument("-d", dest="database", help="Give the database name")
parser.add_argument("-u", dest="user", help="Give the user name")
parser.add_argument("-p", dest="password", help="Give the password within single quotes")
#parser.add_argument("-t", dest="time", help="give the time for the queries")
args = parser.parse_args()

def connect():
    """ Connect to MySQL database """
    try:
        print('Connecting to MySQL database...')
        print"\n\n\n"
        conn = mysql.connector.connect(host=args.host,
                                       database=args.database,
                                       user=args.user,
                                       password=args.password)
        if conn.is_connected():
#first query#
                fo = open("/tmp/reports-mysql/count.txt", "wb")
                cursor = conn.cursor()
                cursor.execute("SELECT HOST FROM INFORMATION_SCHEMA.PROCESSLIST;")
                rows = cursor.fetchall()
                for row in rows:
                        fo.write(str(row[0]).split(":")[0]+"\n")
                fo.close()
                print "\n\n\n"
                ipad = []   # Taking the unique Ip addresses in to a list and appending to array
                unco = []   # taking the count of each unique IP address
                with open('/tmp/reports-mysql/count.txt') as infile:
                     counts = collections.Counter(l.strip() for l in infile)
                for line, count in counts.most_common():
                     ipad.append(line)
                     unco.append(str(count))
                ip_count = zip(ipad, unco)
                ip_count = dict(ip_count)
                connection=ec2.connect_to_region("ap-southeast-1")
                ip_addr_2_names = dict()
                reservations=connection.get_all_instances();
                for reservation in reservations:
                  for instance in reservation.instances:
                        if instance.private_ip_address in ipad:
                                ip_addr_2_names[str(instance.private_ip_address)] = str(instance.tags['Name'])
		host = args.host
                file = host.split(".")
                fo = open("/tmp/reports-mysql/"+file[0]+"-detailed-devops-report"+".txt", "wb")
                fo.write ('#####################total no.of connections###############\n')
                fo.write('\n\n')
                fo.write('Total Connections:'+ str(cursor.rowcount)+"\n")
                fo.write('\n\n')
                for ip in ip_addr_2_names.keys():
                      #  print ip,"\t",ip_addr_2_names[ip],"\t \t",ip_count[ip]
                       fo.write(ip+"\t"+ip_addr_2_names[ip]+"\t"+ip_count[ip]+"\n")
#second query#
                cursor.execute("show slave status;")
                rows = cursor.fetchall()
                columns = cursor.description
		fo.write('\n\n')
                fo.write('########Replication status of the slave#######\n')
                fo.write('Total Row(s):'+ str(cursor.rowcount)+"\n")
                fo.write('\n')

		newList = {}
                for i in range(0,len(rows[0])-1):
			newList[columns[i][0]]=rows[0][i]
		for x,y in newList.items():
			fo.write(str(x) +":"+ str(y)+"\n")

#third query#
                cursor.execute("SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND != 'Sleep';")
                rows = cursor.fetchall()
		fo.write('\n\n')
		fo.write('########Query which is running for more than other than sleep#######\n')
                fo.write('Total Row(s):'+ str(cursor.rowcount)+"\n")
		fo.write('\n')
		for row in rows:
                        t = PrettyTable(['ID', 'USER', 'HOST', 'DB', 'COMMAND', 'TIME', 'STATE', 'INFO'])
                        t.add_row(row)
                        fo.write(str(t))
#forth query#
                cursor.execute("SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND != 'Sleep';")
                rows = cursor.fetchall()
                fo.write('\n\n')
                fo.write('########present running queries#######\n')
                fo.write('Total Row(s):'+ str(cursor.rowcount)+"\n")
                fo.write('\n')
		for row in rows:
                        t = PrettyTable(['ID', 'USER', 'HOST', 'DB', 'COMMAND', 'TIME', 'STATE', 'INFO'])
                        t.add_row(row)
                        fo.write(str(t))
                fo.close()
        else:
            print('connection failed.')

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()
        print('Connection closed.')


if __name__ == '__main__':
    connect()
