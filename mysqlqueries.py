#!/usr/bin/python2.7

# python script to execute mysqlqueries on an RDS instance.

# ./mysqlqueries.py -h

#usage: test.py [-h] [-e HOST] [-d DATABASE] [-u USER] [-p PASSWORD] [-t TIME]

#optional arguments:
#  -h, --help   show this help message and exit
#  -e HOST      Give the RDS instance endpoint
#  -d DATABASE  Give the database name
#  -u USER      Give the user name
#  -p PASSWORD  Give the password within single quotes
#  -t TIME      give the time for the queries

import mysql.connector
from mysql.connector import Error
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-e", dest="host", help="Give the RDS instance endpoint")
parser.add_argument("-d", dest="database", help="Give the database name")
parser.add_argument("-u", dest="user", help="Give the user name")
parser.add_argument("-p", dest="password", help="Give the password within single quotes")
parser.add_argument("-t", dest="time", help="give the time for the queries")
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
                print('Connected to MySQL database')
                print"\n\n\n"
#first query#
                fo = open("foo.txt", "wb")
                cursor = conn.cursor()
                cursor.execute("SELECT HOST FROM INFORMATION_SCHEMA.PROCESSLIST;")
                rows = cursor.fetchall()
                print ('#####################total no.of connections###############')
                print('Total Row(s):', cursor.rowcount)
                fo.write('Total no.of connections\n')
                fo.write('\n\n')
                for row in rows:
#                       print str(row[0]).split(":")[0]
                        fo.write(str(row[0]).split(":")[0]+"\n")
                print "\n\n\n"
#second query#  
                cursor.execute("SHOW STATUS WHERE `variable_name` = 'Threads_connected';")
                rows = cursor.fetchall()

                print('Total Row(s):', cursor.rowcount)
                fo.write('\n\n')
                for row in rows:
#                       print(row)
                        fo.write(str(row)+"\n")
                print"\n\n\n"
#third query#
                cursor.execute("SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND != 'Sleep';")
                rows = cursor.fetchall()

                print('Total Row(s):', cursor.rowcount)
                for row in rows:
                       print(row)
                       fo.write(str(row))
                print"\n\n\n"
#forth query#
                cursor.execute("SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST WHERE Time >= "+args.time+";")
                rows = cursor.fetchall()

                print('Total Row(s):', cursor.rowcount)
                fo.write('\n\n')
                for row in rows:
                       print(row)
                       fo.write(str(row)+"\n")
                print"\n\n\n"
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
