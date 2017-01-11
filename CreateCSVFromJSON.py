import mysql.connector
import json
import sys
from mysql.connector import errorcode

def MySQLConn():
    try:
        conn = mysql.connector.connect(user='root', password='ChangePassword', host='127.0.0.1', database='SmartBiz')
        return conn
    except:
        print("ERROR: Unable to connect to the database running on %s.")
        conn.close()
        sys.exit()

def Main():
    MyDBConn=MySQLConn()
    writeJSONAttrToFile(MyDBConn)


def writeJSONAttrToFile(MyDBConn, jsonDataType):
    SQL="select  page_id, page_type_id,json_extract(extracted_data,'$.%s') as json_data from pages where page_type_id = 62 and status=299" %  jsonDataType
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
