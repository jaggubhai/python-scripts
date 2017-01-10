#!/usr/bin/python2.7

# this python script is a check to see the present running file descriptors on you machine.
# to use this script use help argument like file-descriptors.py -h

# ./filedesc.py -h
#usage: filedesc.py [-h] [-w WARNING] [-c CRITICAL]

#optional arguments:
#  -h, --help   show this help message and exit
#  -w WARNING   Give the file descriptors warning percentage value
#  -c CRITICAL  Give the file descriptors critical percentage value


# ./file-descriptors.py -w 50 -c 60

from __future__ import division
import subprocess
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-w", dest="warning", help="Give the file descriptors warning percentage value")
parser.add_argument("-c", dest="critical", help="Give the file descriptors critical percentage value")
args = parser.parse_args()
if args.warning is None or args.critical is None:
        print "Failed : Please pass both warning and critical arguments. Check help with -h."
        sys.exit()

tfd = subprocess.check_output("cat /proc/sys/fs/file-max", shell=True) #Total File Descriptors
print "Total no.of File Descriptors: " + tfd

hfd = int(tfd) / 2 #Half File Descriptor
#print hfd

ufd = subprocess.check_output("cat /proc/sys/fs/file-nr | awk '{ print $1 }'", shell=True) #Total allocated File Descriptors sb
print "Number of utilized File Descriptors: " + ufd

average = int(ufd)*100 / int(tfd)

print "Percentage of file descriptors used is : " + str(average) + "\n"

if int(average) > int(args.critical):
   print "Utilized file descriptors crossed the critical limit"
   sys.exit(2)
elif int(average) > int(args.warning):
   print "Utilized file descriptors crossed the warning limit"
   sys.exit(1)
else:
   print "Utilized file descriptors are below the warning limit"
   sys.exit(0)
