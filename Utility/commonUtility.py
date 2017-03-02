'''
Created on Jan 10, 2017

@author: Mohandas Damodaran
'''
import string
import base64
import smtplib
from email.mime.text import MIMEText
import time
import os
from time import strftime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64

import mysql.connector
from mysql.connector import errorcode

class Email_Class:
    fromEmail="mohandas@smartbizloans.com"
    toEmail="mohandas@smartbizloans.com"
    emailMessage='Resource cost data load process log'
    def SendEmail(self, Subject, Message=emailMessage, From=fromEmail, To=toEmail ):
        msg = MIMEText(Message)
        msg['Subject'] = Subject
        msg['From'] = From
        msg['To'] = To
        SMTPHost='mail.ad.ge.com'
        s = smtplib.SMTP(SMTPHost)
        s.sendmail(From, To, msg.as_string())
        s.quit()
    def SendEmailWithoutAttachement(self, Subject, FileName, From=fromEmail, To=toEmail):
        Message=open(FileName, "r").read()
        print(Message)
        msg = MIMEText(Message)
        msg['Subject'] = Subject
        msg['From'] = From
        msg['To'] = To
        SMTPHost='mail.ad.ge.com'
        s = smtplib.SMTP(SMTPHost)
        s.sendmail(From, To, msg.as_string())
        s.quit()
    def SendEmailWithAttachement(self, Subject, FileName, From=fromEmail, To=toEmail):
        msg = MIMEMultipart()
        msg['Subject'] = Subject
        msg['From'] = From
        msg['To'] = To
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(FileName, "rb").read())
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename='+FileName)
        msg.attach(part)
        SMTPHost='mail.ad.ge.com'
        s = smtplib.SMTP(SMTPHost)
        s.sendmail(From, To, msg.as_string())
        s.quit()
    def SendEmailWithAttachementFromText(self, Subject, Message, From=fromEmail, To=toEmail):
        msg = MIMEMultipart()
        msg['Subject'] = Subject
        msg['From'] = From
        msg['To'] = To
        part = MIMEBase('application', "octet-stream")
        part.set_payload(Message)
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=UserList.html')
        msg.attach(part)
        SMTPHost='mail.ad.ge.com'
        s = smtplib.SMTP(SMTPHost)
        s.sendmail(From, To, msg.as_string())
        s.quit()

def getConfigData(configFile):
    configFile = open(configFile,'r')
    configData={}
    for line in configFile.readlines():
        pair = line.split(':')
        configData[pair[0]]=pair[1].strip()
    configFile.close()
    return  configData


def EncryptPassword(Passwd):
    return base64.b64encode(Passwd.encode('utf8'))

def DecryptPassword( EncryptedPasswd):
    return base64.b64decode(EncryptedPasswd)

def SortAndRemoveDupFromArray(ArrayList):
    SortedArrayList=sorted(ArrayList)
    from operator import itemgetter
    from itertools import groupby
    unique_list = list(map(itemgetter(0), groupby(SortedArrayList)))
    return unique_list

def GetLogFP(LogLoc):
    if not os.path.exists(LogLoc):
        try:
            os.mkdir(LogLoc)
        except:
            print("ERROR: Couldn't create dir %s." % (LogLoc))
            sendStatusEmail("ERROR in Resource Cost data load process", "Couldn't create the log file dir %s." % LogLoc)
            sys.exit()
    FileName=LogLoc+strftime("%d%b%Y-%H_%M_%S",  time.localtime(time.time()))+'.log'
    fp = open(FileName, 'a')
    return fp,FileName

def executeDBCmd(DBConn, Query, Data):
    try:
        Cursor = DBConn.cursor()
        Cursor.execute(Query, Data)
    except mysql.connector.Error as err:
        printMysqlError(err)
        return False
    return True

def executeDBUpdateCmd(DBConn, Query ):
    try:
        Cursor = DBConn.cursor()
        Cursor.execute(Query)
    except mysql.connector.Error as err:
        printMysqlError(err)
        return False
    return True

def getSingleValFromDB(DBConn, Query):
    cursor = DBConn.cursor()
    cursor.execute (Query)
    row = cursor.fetchone()
    cursor.close()
    if row:
        return row[0]
    else:
        return None

def getMutiColumnFromDB(DBConn, Query):
    cursor = DBConn.cursor()
    cursor.execute (Query)
    row = cursor.fetchone()
    cursor.close()
    if row:
        return row
    else:
        return None

def printMysqlError(err):
    print("Exception: {}".format(err))

