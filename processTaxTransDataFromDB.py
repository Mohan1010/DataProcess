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
    #process_tax_items(MyDBConn)

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

def extractValueWriteToFile(Data, fp, key1, key2, key3=None):
    if isinstance( Data,list):
        for itemvalue in Data:
            fp.write("level3** %s.%s.%s:%s \n" % (key1, key2, key3, itemvalue ))
            break
    else:
        fp.write("level3* %s.%s.%s:%s \n" % ( key1, key2, key3, Data ))
def extractValue(Data, mydict, key1, key2, key3, includeList):
    if isinstance( Data,list):
        for itemvalue in Data:
            itemIndex="%s.%s.%s" % (key1, key2, key3)
            checkAndAddItem(mydict, itemIndex, itemvalue, includeList)
            #mydict[itemIndex]=itemvalue
            break
    else:
        itemIndex="%s.%s.%s" % (key1, key2, key3)
        checkAndAddItem(mydict, itemIndex, Data, includeList)
        #mydict[itemIndex]=Data

def processTaxDataWriteToFile(item, fp, level0id):
    if isinstance(item,str):
        fp.write("level0 Id:: %d %s\n" % ( level0id,item))
    else:
        for mainkey in item.keys():
            if isinstance(item[mainkey],dict):
                subkeyData=item[mainkey]
                for subitem in subkeyData:
                    if isinstance(subkeyData[subitem],dict):
                        subkeyData2=subkeyData[subitem]
                        for subitem2 in subkeyData2:
                            if isinstance(subkeyData2[subitem2],dict):
                                subkeyData3=subkeyData2[subitem2]
                                for subitem3 in subkeyData3:
                                    fp.write("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                            else:
                                extractValue(subkeyData2[subitem2], fp, mainkey, subitem, subitem2)
                    else:
                        if isinstance(subkeyData[subitem],list):
                            transData=subkeyData[subitem]
                            for item4 in subkeyData[subitem]:
                                if isinstance(item4,dict):
                                    for item5 in item4:
                                        extractValue(item4[item5], fp, mainkey, subitem, item5)
                        else:
                            fp.write("level2# %s.%s ::=> %s\n" % (mainkey, subitem, subkeyData[subitem]))
            else:
                fp.write("level1 :: %s:%s\n" % ( mainkey, item[mainkey]))

def processTaxData(item, mydict, includeList, level0id):
    if isinstance(item,str):
        print("level0 Id:: %d %s\n" % ( level0id,item))
    else:
        for mainkey in item.keys():
            if isinstance(item[mainkey],dict):
                subkeyData=item[mainkey]
                for subitem in subkeyData:
                    if isinstance(subkeyData[subitem],dict):
                        subkeyData2=subkeyData[subitem]
                        for subitem2 in subkeyData2:
                            if isinstance(subkeyData2[subitem2],dict):
                                subkeyData3=subkeyData2[subitem2]
                                for subitem3 in subkeyData3:
                                    checkAndAddItem(mydict, subitem3, subkeyData3[subitem3], includeList)
                                    #mydict[subitem3]=subkeyData3[subitem3]
                                    #fp.write("level4  %s:%s\n" % (subitem3, subkeyData3[subitem3]))
                            else:
                                extractValue(subkeyData2[subitem2], mydict, mainkey, subitem, subitem2, includeList)
                    else:
                        if isinstance(subkeyData[subitem],list):
                            transData=subkeyData[subitem]
                            for item4 in subkeyData[subitem]:
                                if isinstance(item4,dict):
                                    for item5 in item4:
                                        extractValue(item4[item5], mydict, mainkey, subitem, item5, includeList)
                        else:

                            itemIndex="%s.%s" % (mainkey, subitem)
                            checkAndAddItem(mydict, itemIndex, subkeyData[subitem], includeList)
                            #mydict[itemIndex]=subkeyData[subitem]
            else:
                checkAndAddItem(mydict, mainkey, item[mainkey], includeList)
                #mydict[mainkey]=item[mainkey]
def checkAndAddItem(mydict, itemIndex, itemvalue, includeList):
    if itemIndex in includeList:
        mydict[itemIndex]=itemvalue

def processTax_return_personals(MyDBConn):
    uniqueTaxValues= dict()
    dwNeededList=[]
    collectDistinctTaxItemsTobeProcessed( MyDBConn,dwNeededList )
    SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE id=5888"
    #SQL="SELECT id,guarantor_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_return_personals WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '
    taxDataDict={}
    #fp = open("./PersonalTaxData.info", 'w')
    for row in rows:
        cnt = cnt + 1
        my_json_dict = json.loads(row[7])
        for item in my_json_dict:
            taxDataDict={}
            processTaxData(item, taxDataDict, dwNeededList, row[0])
            for myItem in taxDataDict:
                print("%s:%s\n" % (myItem, taxDataDict[myItem]))
    print("Count: %d" % cnt)

    MyDBConn.commit()
    #fp.close()
    cur.close()

def insertIntoDataStruct(name,dictType, uniqueTaxValues):
    if not name in uniqueTaxValues:
        uniqueTaxValues[name]=(dictType)
def collectDistinctTaxItemsTobeProcessed(MyDBConn, myList):
    SQL="SELECT item FROM dw_staging.Tax_Items WHERE needed_for_dw=1"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    for row in rows:
        if not row[0] in myList:
            myList.insert(0,row[0])



def processTax_return_business(MyDBConn):
    uniqueTaxValues= dict()
    dwNeededList=[]
    collectDistinctTaxItemsTobeProcessed( MyDBConn,dwNeededList )
    SQL="SELECT id,business_id,year,name,form_id,filing_id,second_name, obfuscated_transcript FROM tax_returns WHERE obfuscated_transcript IS NOT NULL ORDER BY id DESC LIMIT 1"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    data=' '

    taxDataDict={}
    for row in rows:
        cnt = cnt + 1
        item = json.loads(row[7])
        processTaxData(item, taxDataDict, dwNeededList, row[0])
    for item in taxDataDict:
        print("%s:%s\n" % (item, taxDataDict[item]))
    print("Count: %d" % cnt)

    MyDBConn.commit()
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

def process_tax_items(MyDBConn):
    #Delete Data from dw_staging.Tax_Items
    #Run "INSERT INTO Tax_Items(item,item_type) SELECT item_name,'Personal' FROM dw.personal_tax_items;" from mysql command line.
    SQL="SELECT item_name FROM dw.business_tax_items"
    cur = MyDBConn.cursor()
    cur2 = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cur3 = MyDBConn.cursor()
    for row in rows:
        SQL2="SELECT item FROM dw_staging.Tax_Items WHERE item='%s'" % row[0]

        cur2.execute(SQL2)
        rows2 = cur2.fetchall()
        cnt=0
        for row2 in rows2:
            cnt = cnt + 1
            cur3.execute("UPDATE dw_staging.Tax_Items set item_type='Both' WHERE item='%s'" % row2[0])
        if cnt == 0:
            cur3.execute("INSERT INTO dw_staging.Tax_Items(item,item_type) VALUES('%s','Business')" % row[0])

    MyDBConn.commit()
    cur.close()

if __name__ == '__main__':
    Main()
