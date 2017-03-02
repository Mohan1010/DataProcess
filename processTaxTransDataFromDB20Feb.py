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
    processTax_return_personals(MyDBConn)
    processTax_return_business(MyDBConn)

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

def extractValue(Data, fp, key1, key2, key3=None):
    if isinstance( Data,list):
        for itemvalue in Data:
            fp.write("level3** %s.%s.%s:%s \n" % (key1, key2, key3, itemvalue ))
            break
    else:
        fp.write("level3* %s.%s.%s:%s \n" % ( key1, key2, key3, Data ))

def processTax_return_personals(MyDBConn):
    uniqueTaxValues= dict()
    #SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE id=5888"

    SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    fp = open("./PersonalTaxData.info", 'w')
    for row in rows:
        cnt = cnt + 1
        obfuscated_transcript=row[7]
        my_json_dict = json.loads(obfuscated_transcript)
        for item in my_json_dict:
            #print("schedule_c_profit_or_loss_from_business.expenses.car_and_truck_expenses :: %s" % item['schedule_c_profit_or_loss_from_business']['expenses']['car_and_truck_expenses'])
            if isinstance(item,str):
                fp.write("level0 Id:: %d %s\n" % ( row[0],item))
            else:
                for mainkey in item.keys():
                    #print("%s <=> %s" % (mainkey, type(item[mainkey]) ))
                    if isinstance(item[mainkey],dict):
                        subkeyData=item[mainkey]
                        for subitem in subkeyData:
                            if isinstance(subkeyData[subitem],dict):
                                subkeyData2=subkeyData[subitem]
                                for subitem2 in subkeyData2:
                                    if isinstance(subkeyData2[subitem2],dict):
                                        subkeyData3=subkeyData2[subitem2]

                                        for subitem3 in subkeyData3:
                                            #print("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                                            fp.write("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                                    else:
                                        extractValue(subkeyData2[subitem2], fp, mainkey, subitem, subitem2)
                                        #if isinstance( subkeyData2[subitem2],list):
                                        #    for itemvalue in subkeyData2[subitem2]:
                                        #        print("level3* %s.%s.%s:%s \n" % (mainkey, subitem, subitem2, itemvalue ))
                                        #        break
                                        #else:
                                        #    print("level3* %s.%s.%s:%s \n" % (mainkey, subitem, subitem2, subkeyData2[subitem2] ))
                            else:
                                if isinstance(subkeyData[subitem],list):
                                    transData=subkeyData[subitem]
                                    for item4 in subkeyData[subitem]:
                                        if isinstance(item4,dict):
                                            for item5 in item4:
                                                extractValue(item4[item5], fp, mainkey, subitem, item5)
                                                #fp.write("level3# %s.%s.%s:%s\n" % (mainkey, subitem, item5, item4[item5] ))
                                else:
                                    fp.write("level2# %s.%s ::=> %s\n" % (mainkey, subitem, subkeyData[subitem]))
                    else:
                        fp.write("level1 :: %s:%s\n" % ( mainkey, item[mainkey]))
    print("Count: %d" % cnt)

    MyDBConn.commit()
    fp.close()
    cur.close()

def processTax_return_business(MyDBConn):
    uniqueTaxValues= dict()
    #SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE id=5888"
    SQL="SELECT id,business_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_returns WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    fp = open("./BusinessTaxData.info", 'w')
    for row in rows:
        cnt = cnt + 1
        obfuscated_transcript=row[7]
        #fp.write(obfuscated_transcript)
        item = json.loads(obfuscated_transcript)
        #for item in my_json_dict:
        #print("schedule_c_profit_or_loss_from_business.expenses.car_and_truck_expenses :: %s" % item['schedule_c_profit_or_loss_from_business']['expenses']['car_and_truck_expenses'])
        if isinstance(item,str):
            fp.write("level0 Id:: %d %s\n" % ( row[0],item))
        else:
            for mainkey in item.keys():
                #print("%s <=> %s" % (mainkey, type(item[mainkey]) ))
                if isinstance(item[mainkey],dict):
                    subkeyData=item[mainkey]
                    for subitem in subkeyData:
                        if isinstance(subkeyData[subitem],dict):
                            subkeyData2=subkeyData[subitem]
                            for subitem2 in subkeyData2:
                                if isinstance(subkeyData2[subitem2],dict):
                                    subkeyData3=subkeyData2[subitem2]

                                    for subitem3 in subkeyData3:
                                        #print("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                                        fp.write("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                                else:
                                    extractValue(subkeyData2[subitem2], fp, mainkey, subitem, subitem2)
                                    #if isinstance( subkeyData2[subitem2],list):
                                    #    for itemvalue in subkeyData2[subitem2]:
                                    #        print("level3* %s.%s.%s:%s \n" % (mainkey, subitem, subitem2, itemvalue ))
                                    #        break
                                    #else:
                                    #    print("level3* %s.%s.%s:%s \n" % (mainkey, subitem, subitem2, subkeyData2[subitem2] ))
                        else:
                            if isinstance(subkeyData[subitem],list):
                                transData=subkeyData[subitem]
                                for item4 in subkeyData[subitem]:
                                    if isinstance(item4,dict):
                                        for item5 in item4:
                                            extractValue(item4[item5], fp, mainkey, subitem, item5)
                                            #extractValue(item5, fp, mainkey, subitem, item5)
                                            #fp.write("level3# %s.%s.%s:%s\n" % (mainkey, subitem, item5, item4[item5] ))
                            else:
                                fp.write("level2# %s.%s ::=> %s\n" % (mainkey, subitem, subkeyData[subitem]))
                else:
                    fp.write("level1 :: %s:%s\n" % ( mainkey, item[mainkey]))
    print("Count: %d" % cnt)

    MyDBConn.commit()
    fp.close()
    cur.close()

def processTax_return_businessOld(MyDBConn):
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
