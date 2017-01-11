'''
Created on Jan 10, 2017

@author: Mohandas Damodaran
'''
import mysql.connector
import json
import sys,os
import time
from time import strftime
from mysql.connector import errorcode
from Utility import commonUtility
class Global:
    configData=commonUtility.getConfigData('/home/mohandas/Config.dat')
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
        print GV.User, GV.DBPassword, GV.Host, GV.DataBase
        conn = mysql.connector.connect(user=GV.User, password=GV.DBPassword, host=GV.Host, database=GV.DataBase)
        return conn
    except:
        print("ERROR: Unable to connect to the database running on %s." % GV.Host)
        sys.exit()

def Main(jsonDataType):
    MyDBConn=MySQLConn()
    writeJSONAttrToFile(MyDBConn,jsonDataType)


def writeJSONAttrToFile(MyDBConn, jsonDataType):
    SQL="SELECT page_id, page_type_id, json_extract(extracted_data,'$.%s') AS json_data FROM pages WHERE page_type_id = 62 AND status=299" %  jsonDataType
    try:
        fp = open("/home/mohandas/json_attributes.csv", 'w')
        cur = MyDBConn.cursor()
        cur.execute(SQL)
        rows = cur.fetchall()
        cnt=0
        Header="page_id, page_type_id"
        for row in rows:
            DataLine=str(row[0])+","+str(row[1])
            data = json.loads(row[2])
            #DataLineCnt=0
            for key, value in data.items():
                tempValue= json.loads(str(value).replace("u'", "'").replace("'",'"'))
                for key2, value2 in tempValue.items():
                    if key2 != "height":
                        DataLine = DataLine + ","+str(value2)
                        if cnt == 0:
                            Header = Header + "," + key + "_" + key2

            if cnt == 0:
                fp.write(Header+"\n")
            fp.write(DataLine+"\n")
            cnt = 1
        fp.close()
        cur.close()
    except Exception, e:
        print(str(e) )
        return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        Main(sys.argv[1] )
    else:
        Main("step_detail")