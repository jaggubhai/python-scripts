#!/usr/bin/python2.7

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

user = '' #Give ses user with in the single quotes (Smtpusername)
pw   = '' # Give ses password with in the single quotes (Smtppassowrd) 
host = ''  # Give ses smtp host deatils with in the single quotes (email-smtp.us-north-1.amazonaws.com)
port = 465
fromaddr = "" # Give from address
toaddr = "" # Give to address
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Python script in sending an email with attacment"

body = "Please find the attached text file"
msg.attach(MIMEText(body, 'plain'))

filename = "file.txt"
attachment = open("/home/vagrant/file.txt", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP_SSL(host, port, 'swiggy.com')
server.set_debuglevel(1)
server.login(user, pw)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
