#!/usr/bin/python2.7


# this python script is for couting the connections that are connected to an RDS instance along with their names and private IP address and total no.of connection made by a single ec2 instances.

# Example : private IP address  ec2-instancename  count(no.of connections made to an RDS instance)

#Usage:

# ./RDSConnections.py -h
#usage: ipcollection.py [-h] [-e HOST] [-d DATABASE] [-u USER] [-p PASSWORD]

#optional arguments:
#  -h, --help   show this help message and exit
#  -e HOST      Give the RDS instance endpoint
#  -d DATABASE  Give the database name
#  -u USER      Give the user name
#  -p PASSWORD  Give the password within single quotes


import mysql.connector
from mysql.connector import Error
import argparse
import subprocess
import boto
from boto import ec2
import collections

parser = argparse.ArgumentParser()
parser.add_argument("-e", dest="host", help="Give the RDS instance endpoint")
parser.add_argument("-d", dest="database", help="Give the database name")
parser.add_argument("-u", dest="user", help="Give the user name")
parser.add_argument("-p", dest="password", help="Give the password within single quotes")
args = parser.parse_args()

def connect():
    """ Connect to MySQL database """
    try:
	print('Connecting to MySQL database...')
	print"\n"
        conn = mysql.connector.connect(host=args.host,
                                       database=args.database,
                                       user=args.user,
                                       password=args.password)
        if conn.is_connected():
            	print('Connected to MySQL database')
		print"\n"
#first query#
                fo = open("foo.txt", "wb+")
		cursor = conn.cursor()
		cursor.execute("SELECT HOST FROM INFORMATION_SCHEMA.PROCESSLIST;")
        	rows = cursor.fetchall()
	   	print ('#####################total no.of connections###############')
	        print('Total Row(s):', cursor.rowcount)
		print"\n"
        	for row in rows:
			fo.write(str(row[0]).split(":")[0]+"\n")
		fo.close()
		ipd = [] #
		occ = []
       		with open('foo.txt') as infile:
    		     counts = collections.Counter(l.strip() for l in infile)
                for line, count in counts.most_common():
		     ipd.append(line) # appended IP address to ipd
		     occ.append(str(count)) # appended IP address count to occ
                ip_count = zip(ipd, occ)
		ip_count = dict(ip_count)

		connection=ec2.connect_to_region("ap-southeast-1")
		ip_addr_2_names = dict()
		reservations=connection.get_all_instances();
	        for reservation in reservations:
		  for instance in reservation.instances:
			if instance.private_ip_address in ipd:
				ip_addr_2_names[str(instance.private_ip_address)] = str(instance.tags['Name'])

		for ip in ip_addr_2_names.keys():
			print ip,"\t",ip_addr_2_names[ip],"\t",ip_count[ip]
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



