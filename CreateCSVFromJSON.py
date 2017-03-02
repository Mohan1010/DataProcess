'''
Created on Jan 10, 2017

@author: Mohandas Damodaran
'''
import mysql.connector
import simplejson as json
import sys,os
import time
from time import strftime
from mysql.connector import errorcode
from Utility import commonUtility
class Global:
    configData=commonUtility.getConfigData('./Config.dat')
    User=configData["User"]
    Host=configData["Host"]
    DataBase=configData["DataBase"]
    DBPassword=commonUtility.DecryptPassword(configData["DBPassword"])
    LogLoc=configData["LogLoc"]
    logFP,logFileName=commonUtility.GetLogFP(LogLoc)

def closeLogFP():
    GV.logFP.close()

GV = Global()
def MySQLConn():
    try:
        print (GV.User, GV.DBPassword, GV.Host, GV.DataBase)
        conn = mysql.connector.connect(user=GV.User, host=GV.Host, database=GV.DataBase)
        return conn
    except:
        print("ERROR: Unable to connect to the database running on %s." % GV.Host)
        sys.exit()

def Main():
    MyDBConn=MySQLConn()
    processTax_return_personals2(MyDBConn)
    #processTax_return_business(MyDBConn)

def item_generator_find(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.iteritems():
            if k == lookup_key:
                yield v
            else:
                for child_val in item_generator_find(v, lookup_key):
                    yield child_val
    elif isinstance(json_input, list):
        for item in json_input:
            for item_val in item_generator_find(item, lookup_key):
                yield item_val

def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.iteritems():
            if k == lookup_key:
                yield v
            else:
                for child_val in item_generator(v, lookup_key):
                    yield child_val
    elif isinstance(json_input, list):
        for item in json_input:
            for item_val in item_generator(item, lookup_key):
                yield item_val

def flattenDict(d,result=None,index=None,Key=None):
    if result is None:
        result = {}
    if isinstance(d, (list, tuple)):
        for indexB, element in enumerate(d):
            if Key is not None:
                newkey = Key
            flattenDict(element,result,index=indexB,Key=newkey)
    elif isinstance(d, dict):
        for key in d:
            value = d[key]
            if Key is not None and index is not None:
                newkey = ".".join([Key,(str(key).replace(" ", "") + str(index))])
            elif Key is not None:
                newkey = ".".join([Key,(str(key).replace(" ", ""))])
            else:
                newkey= str(key).replace(" ", "")
            flattenDict(value,result,index=None,Key=newkey)
    else:
        result[Key]=d
    return result

def insertIntoDataStruct(name,dictType, uniqueTaxValues):
    if not name in uniqueTaxValues:
        uniqueTaxValues[name]=(dictType)

def insert_personal_tax_items(item_name, cursor):
    query = "INSERT INTO dw.personal_tax_items(item_name) VALUES ('"+ item_name +"' )"
    try:
        cursor.execute(query)
        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')
    except Error as error:
        print(error)

def insert_business_tax_items(item_name, cursor):
    query = "INSERT INTO dw.business_tax_items(item_name) VALUES ('"+ item_name +"' )"
    try:
        cursor.execute(query)
        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')
    except Error as error:
        print(error)

def processTax_return_personals(MyDBConn):
    uniqueTaxValues= dict()
    SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC LIMIT 1"
    fp = open("./PersonalTaxReturns.csv", 'w')
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    for row in rows:
        print(row[0])
        obfuscated_transcript=row[7]
        data = json.loads(obfuscated_transcript)
        #data2=data["result"]
        for item in data:
            if isinstance(item,dict):
                item2= flattenDict(item)
                for item3 in item2:
                    print("%s\n" % item3)
                    insertIntoDataStruct(item3, type(item2[item3]), uniqueTaxValues)
    for value in uniqueTaxValues:
        fp.write("%s :: %s" %(value, uniqueTaxValues[value]))
        #insert_personal_tax_items(value, cur)

    MyDBConn.commit()
    fp.close()
    cur.close()

def processTax_return_personals2(MyDBConn):
    uniqueTaxValues= dict()
    SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC LIMIT 1"
    fp = open("./PersonalTaxReturns.csv", 'w')
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    for row in rows:
        print(row[0])
        obfuscated_transcript=row[7]
        data = json.loads(obfuscated_transcript)
        print("%s" % data)
        #data2=data["result"]
        #for item in data:
        #    print("%s" % item.split(","))
        #    for myitem in item.split("\n"):
        #        print("%s" % myitem)
        #insert_personal_tax_items(value, cur)

    MyDBConn.commit()
    fp.close()
    cur.close()
def processTax_return_business(MyDBConn):
    uniqueBusinessTaxValues= dict()
    SQL="SELECT id, business_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_returns WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC LIMIT 1"
    fp = open("./BusinessTaxReturns.csv", 'w')
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    for row in rows:
        obfuscated_transcript=row[7]
        item = json.loads(obfuscated_transcript)
        if isinstance(item,dict):
            item2= flattenDict(item)
            for item3 in item2:
                insertIntoDataStruct(item3, type(item2[item3]), uniqueBusinessTaxValues)
        else:
            print("Not dict")
    for value in uniqueBusinessTaxValues:
        fp.write("%s :: %s" %(value, uniqueBusinessTaxValues[value]))
        #insert_business_tax_items(value, cur)

    MyDBConn.commit()
    fp.close()
    cur.close()

if __name__ == '__main__':
    Main()
