'''
Created on Feb 25, 2017

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

def runLog(message, printMessage=True):
    localtime=strftime("%d %b %Y %H:%M:%S",  time.localtime(time.time()))
    if printMessage:
        print (localtime+":-:"+str(message))
    GV.logFP.write(localtime+":-:"+str(message) +"\n")

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

def create_insert_stmts(MyDBConn):
    SQL="SELECT table_name, column_name FROM information_schema.columns WHERE  table_schema = 'dw_staging' ORDER BY 1,2"
    cur = MyDBConn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    valueFormat=''
    fp = open("DBScripts/Insert.sql", 'w')
    tableName=' '
    for row in rows:
        if tableName != row[0]:
            if cnt > 0:
                fp.write("SELECT %s  FROM dw_source.%s\n" % (columns, tableName ))
                fp.write("INSERT INTO dw_staging." + tableName + "("+ columns + ")"+" VALUES( "+ valueFormat+ ") % ("+ ColValues +")\n")
                cnt=0
            tableName = row[0]
            columns = row[1]
            valueFormat="'%s'"
            ColValues="row[\"%s\"]" % row[1]
            cnt = cnt + 1
        else:
            columns = columns +","+ row[1]
            ColValues = ColValues +","+ "row[\"%s\"]" % row[1]
            valueFormat = valueFormat +","+ "'%s'"
            cnt = cnt + 1
    fp.close()

def loadUsersFromSource(MyDBConn, updatedAt):
    runLog("Loading data from users.")
    if updatedAt is not None:
        selectSQL="SELECT first_name,last_name,email,phone, id as id_from_source, created_at, updated_at from dw_source.users WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT first_name,last_name,email,phone, id as id_from_source, created_at, updated_at from dw_source.users"
    cur = MyDBConn.cursor()
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        cnt = cnt + 1
        firstName=row[0]
        lastName=row[1]
        if firstName is not None:
            firstName=firstName.replace("'","''")
        if lastName is not None:
            lastName=lastName.replace("'","''")
        insORupdate="I"
        if updatedAt is not None:
            person_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.persons WHERE id_from_source=%d AND source_table='users' " %  row[4] )
            if person_id is not None:
                insORupdate='U'
        if insORupdate == "I":
            #print("Inserting %s, %s , %s" % (firstName, lastName, row[4]) )
            insCur.execute("INSERT INTO dw_staging.persons ( first_name,last_name,email,phone, person_type, sources_id, id_from_source, source_table, admin, created_at, updated_at )"+\
                       "VALUES ('%s', '%s', '%s', '%s', '%s', %d, %d, '%s', %d, '%s', '%s')"
                       %(firstName, lastName, row[2].replace("'","''"), row[3], 'User', 1, row[4], 'users', 0, row[5], row[6] ))
        else:
            runLog("Updating %s, %s , %s" % (firstName, lastName, row[4]) )
            insCur.execute("UPDATE dw_staging.persons SET first_name='%s',last_name='%s', email = '%s', phone='%s', updated_at='%s' WHERE id=%d"
                       %(firstName, lastName, row[2].replace("'","''"), row[3], row[6], person_id ) )

    print("%d records processed." % cnt)
    MyDBConn.commit()

def loadAdminsFromSource(MyDBConn, updatedAt):
    runLog("Loading data from admins.")
    if updatedAt is not None:
        selectSQL="SELECT first_name,last_name,email,phone,  id as id_from_source, created_at, updated_at from dw_source.admins WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT first_name,last_name,email,phone,  id as id_from_source, created_at, updated_at from dw_source.admins"
    cur = MyDBConn.cursor()
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        cnt = cnt + 1
        firstName=row[0]
        lastName=row[1]
        if firstName is not None:
            firstName=firstName.replace("'","''")
        if lastName is not None:
            lastName=lastName.replace("'","''")
        insORupdate="I"
        if updatedAt is not None:
            person_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.persons WHERE id_from_source=%d AND source_table='admins' " %  row[4] )
            if person_id is not None:
                insORupdate='U'
        if insORupdate == "I":
            insCur.execute("INSERT INTO dw_staging.persons ( first_name,last_name,email,phone, person_type, sources_id, id_from_source, source_table, admin, created_at, updated_at )"+\
                       "VALUES ('%s', '%s', '%s', '%s', '%s', %d, %d, '%s', %d, '%s', '%s')"
                       %(firstName, lastName, row[2].replace("'","''"), row[3], 'User', 1, row[4], 'admins', 1, row[5], row[6]));
        else:
            runLog("Updating %s, %s , %s" % (firstName, lastName, row[4]) )
            insCur.execute("UPDATE dw_staging.persons SET first_name='%s',last_name='%s', email = '%s', phone='%s', updated_at='%s' WHERE id=%d "
                       %(firstName, lastName, row[2].replace("'","''"), row[3], row[6], person_id ) )
    runLog("%d records processed." % cnt)
    MyDBConn.commit()

def checkAndInsertAddress(MyDBConn, row):
    SQL="SELECT id FROM dw_staging.addresses WHERE street='%s' AND city = '%s' AND state = '%s' AND zip='%s' AND apt='%s' "
    insCur = MyDBConn.cursor()
    street = row[5]
    if street is not None:
        street=street.replace("'","''")
    city = row[1]
    if city is not None:
        city=city.replace("'","''")
    apt = row[0]
    if apt is not None:
        apt=apt.replace("'","''")
    #print("'%s' '%s' '%s' '%s' '%s'" % ( street,  city, row[4], row[7], apt  ))
    addrId=commonUtility.getSingleValFromDB( MyDBConn, SQL % (street,  city, row[4], row[7], apt ))
    if addrId is None:
        insCur.execute("INSERT INTO dw_staging.addresses "+\
        "(apt,city,created_at,id_from_source,sources_id,source_table,state,street,updated_at,zip) VALUES "+\
        "('%s', '%s','%s', %d, %d, '%s', '%s', '%s', '%s', '%s' )" % ( apt,city,row[2],row[3],1, 'addresses', row[4], street,row[6],row[7] ))
        return insCur.lastrowid
    else:
        return addrId

def loadGuarantorsFromSource(MyDBConn, updatedAt):
    runLog("Loading data from guarantors.")
    if updatedAt is not None:
        selectSQL="SELECT first_name, middle_name, last_name, gender, email, home_phone, mobile_phone, citizenship, id AS id_from_source, created_at, updated_at FROM dw_source.guarantors WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT first_name,middle_name, last_name, gender, email, home_phone, mobile_phone, citizenship, id AS id_from_source, created_at, updated_at FROM dw_source.guarantors"
    addressSQL="SELECT apt,city,created_at,id as id_from_source,state,street,updated_at,zip, IF(type IS NOT NULL,SUBSTR(type,INSTR(type,'::')+2),type) as type FROM dw_source.addresses WHERE addressable_type ='Guarantor' AND addressable_id = '%s' limit 1"
    cur = MyDBConn.cursor()
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    person_id=None
    for row in rows:
        cnt = cnt + 1
        firstName=row[0]
        middleName=row[1]
        lastName=row[2]
        email=row[4]
        addrSQL=addressSQL % row[8]
        if firstName is not None:
            firstName=firstName.replace("'","''")
        if middleName is not None:
            middleName=middleName.replace("'","''")
        if lastName is not None:
            lastName=lastName.replace("'","''")
        if email is not None:
            email=email.replace("'","''")
        insORupdate="I"
        if updatedAt is not None:
            person_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.persons WHERE id_from_source=%d AND source_table='guarantors' " %  row[8] )
            if person_id is not None:
                insORupdate='U'
        if insORupdate == "I":
            #print("Inserting %s, %s,%s , %s" % (firstName, middleName, lastName, row[8],) )
            insCur.execute("INSERT INTO dw_staging.persons ( first_name,middle_name, last_name, person_type, gender, email, phone, mobile_phone, citizenship, id_from_source, source_table, admin, created_at, updated_at, sources_id ) " +\
                           "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', '%s', %d)"
                           %(firstName, middleName, lastName, 'Guarantor', row[3], email, row[5], row[6], row[7], row[8],  'guarantors', 0, row[9], row[10], 1));
            person_id=insCur.lastrowid
            addressRow = commonUtility.getMutiColumnFromDB(MyDBConn, addrSQL)
            if addressRow is not None:
                addressId = checkAndInsertAddress( MyDBConn, addressRow )
                insCur.execute("INSERT INTO dw_staging.person_business_addresses (address_id, addressable_type, business_person_id, address_type)"+\
                           " VALUES(%d, '%s',%d,'%s')" % ( addressId, 'Persons', person_id, addressRow[8] ));
        else:
            #print("Updating %s, %s,%s , %s" % (firstName, middleName, lastName, row[8],) )
            insCur.execute("UPDATE dw_staging.persons SET first_name = '%s',middle_name='%s', last_name='%s', gender='%s', email='%s', phone='%s', mobile_phone='%s', citizenship='%s',  updated_at='%s' WHERE id=%d"
                           %( firstName, middleName, lastName, row[3], email, row[5], row[6], row[7], row[10], person_id ))
            addressRow = commonUtility.getMutiColumnFromDB(MyDBConn, addrSQL)
            if addressRow is not None:
                addressId = checkAndInsertAddress( MyDBConn, addressRow )
                pbAddrInfo= commonUtility.getMutiColumnFromDB(MyDBConn, "SELECT id, address_id FROM dw_staging.person_business_addresses WHERE business_person_id=%d AND addressable_type='Persons' " % person_id )
                if pbAddrInfo[1] != addressId:
                    print("Updating address ")
                    commonUtility.executeDBUpdateCmd(MyDBConn, "UPDATE dw_staging.person_business_addresses SET active=0 WHERE id=%d" % pbAddrInfo[1] )
                    insCur.execute("INSERT INTO dw_staging.person_business_addresses (address_id, addressable_type, business_person_id, address_type)"+\
                           " VALUES(%d, '%s',%d,'%s')" % ( addressId, 'Persons', person_id, addressRow[8] ));
    runLog("%d records processed." % cnt)
    MyDBConn.commit()

def loadBusinessesFromSource(MyDBConn, updatedAt):
    runLog("Loading data from business.")
    if updatedAt is not None:
        #.                  0          1         2                3.  4           5               6        7          8          9
        selectSQL="SELECT created_at, fax, fiscal_year_end_date, id, name, IFNULL(employees,0) , phone, trade_name, updated_at, loan_id, industry_id FROM dw_source.businesses WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT created_at, fax, fiscal_year_end_date, id, name, IFNULL(employees,0) , phone, trade_name, updated_at, loan_id, industry_id FROM dw_source.businesses"
    addressSQL="SELECT apt,city,created_at,id as id_from_source,state,street,updated_at,zip, "+\
    " IF(type IS NOT NULL,SUBSTR(type,INSTR(type,'::')+2),type) as type FROM dw_source.addresses "+\
    "WHERE addressable_type ='Business' AND addressable_id = '%s' limit 1"
    cur = MyDBConn.cursor()
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    business_id=None
    for row in rows:
        cnt = cnt + 1
        Name=row[4]
        tradeName=row[7]
        addrSQL=addressSQL % row[3]
        if Name is not None:
            Name=Name.replace("'","''")
        if tradeName is not None:
            tradeName=tradeName.replace("'","''")
        insORupdate="I"
        if updatedAt is not None:
            business_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.businesses WHERE id_from_source=%d AND source_table='businesses' " %  row[3] )
            if business_id is not None:
                insORupdate='U'
        if insORupdate == "I":
        #print("'%s', '%s', '%s', %s, '%s', %s, '%s', %s, '%s', '%s', '%s'" % (row[0],  row[1], row[2], row[3], Name, row[5], row[6],1, 'businesses', tradeName, row[8] ))
            insCur.execute("INSERT INTO dw_staging.businesses (created_at, fax, fiscal_year_end_date, id_from_source, name, no_of_employees, phone,sources_id,source_table,trade_name,updated_at, industry_id) " +\
                           "VALUES ('%s', '%s', '%s', %d, '%s', %d, '%s', %d, '%s', '%s', '%s', '%s')"
                           % (row[0],  row[1], row[2], row[3], Name, row[5], row[6],1, 'businesses', tradeName, row[8], row[10] ));
            business_id=insCur.lastrowid
            addressRow = commonUtility.getMutiColumnFromDB(MyDBConn, addrSQL)
            if addressRow is not None:
                addressId = checkAndInsertAddress( MyDBConn, addressRow )
                insCur.execute("INSERT INTO dw_staging.person_business_addresses (address_id, addressable_type, business_person_id, address_type)"+\
                           " VALUES(%d, '%s',%d,'%s')" % ( addressId, 'Businesses', business_id, addressRow[8] ));
            insCur.execute("INSERT INTO dw_staging.loan_business_info (business_id,loan_id) VALUES(%s, '%s')" % (business_id, row[9]) )
        else:
            insCur.execute("UPDATE dw_staging.businesses SET fax='%s', fiscal_year_end_date='%s', name='%s', no_of_employees=%s, phone ='%s',trade_name='%s',updated_at='%s', industry_id=%s WHERE id=%d"
                           %( row[1], row[2], Name, row[5], row[6], tradeName, row[8], row[10], business_id ))
            addressRow = commonUtility.getMutiColumnFromDB(MyDBConn, addrSQL)
            if addressRow is not None:
                addressId = checkAndInsertAddress( MyDBConn, addressRow )
                pbAddrInfo= commonUtility.getMutiColumnFromDB(MyDBConn, "SELECT id, address_id FROM dw_staging.person_business_addresses WHERE business_person_id=%d AND addressable_type='Businesses' " % business_id )
                if pbAddrInfo[1] != addressId:
                    print("Updating address ")
                    commonUtility.executeDBUpdateCmd(MyDBConn, "UPDATE dw_staging.person_business_addresses SET active=0 WHERE id=%d" % pbAddrInfo[1] )
                    insCur.execute("INSERT INTO dw_staging.person_business_addresses (address_id, addressable_type, business_person_id, address_type)"+\
                           " VALUES(%d, '%s',%d,'%s')" % ( addressId, 'Persons', business_id, addressRow[8] ));

    runLog("%d records inserted." % cnt)
    MyDBConn.commit()

def checkAndInsertAddress2(MyDBConn, street, city, state, zip, created_at, updated_at, id_from_source ):
    SQL="SELECT id FROM dw_staging.addresses WHERE street='%s' AND city = '%s' AND state = '%s' AND zip='%s'"
    insCur = MyDBConn.cursor()
    if street is not None:
        street=street.replace("'","''")
    if city is not None:
        city=city.replace("'","''")
    addrId=commonUtility.getSingleValFromDB( MyDBConn, SQL % (street, city, state, zip ))
    if addrId is None:
        insCur.execute("INSERT INTO dw_staging.addresses "+\
        "(city,created_at,id_from_source,sources_id,source_table,state,street,updated_at,zip) VALUES "+\
        "('%s','%s', %d, %d, '%s', '%s', '%s', '%s', '%s' )" % ( city,created_at,id_from_source,1, 'lenders', state,street,updated_at,zip ))
        return insCur.lastrowid
    else:
        return addrId

def loadLendersFromSource(MyDBConn, updatedAt):
    runLog("Loading data from lenders.")
    if updatedAt is not None:
        selectSQL="SELECT created_at, credit_score_provider, id, identifier, manual_max, manual_min, name, name_short, type, updated_at, contact_first_name, contact_last_name, "+\
                "contact_phone, contact_fax, address, city, state, zip  FROM dw_source.lenders WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT created_at, credit_score_provider, id, identifier, manual_max, manual_min, name, name_short, type, updated_at, contact_first_name, contact_last_name, "+\
                "contact_phone, contact_fax, address, city, state, zip  FROM dw_source.lenders"
        #  0              1                 2       3          4         5          6       7          8       9           10                11                 12              13           14.    15.    16.  17
        #created_at, credit_score_provider, id, identifier, manual_max, manual_min, name, name_short, type, updated_at, contact_first_name, contact_last_name, contact_phone, contact_fax, address, city, state, zip
    cur = MyDBConn.cursor()
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        cnt = cnt + 1
        Name=row[6]
        shortName=row[7]
        contactFName=row[10]
        contactLName=row[11]
        if Name is not None:
            Name=Name.replace("'","''")
        if shortName is not None:
            shortName=shortName.replace("'","''")
        if contactFName is not None:
            contactFName=contactFName.replace("'","''")
        if contactLName is not None:
            contactLName=contactLName.replace("'","''")
        addressId = checkAndInsertAddress2( MyDBConn, row[14], row[15], row[16], row[17], row[0], row[9], row[2] )
        insORupdate="I"
        if updatedAt is not None:
            lender_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.lenders WHERE id=%d " %  row[2] )
            if lender_id is not None:
                insORupdate='U'
        if insORupdate == "I":
            lender_id=row[2]
            insCur.execute("INSERT INTO dw_staging.lenders (id, address_id, contact_fax, contact_first_name, contact_last_name, contact_phone, "+\
                    "created_at,credit_score_provider, identifier,manual_max,manual_min,name,name_short,type,updated_at) " +\
                    "VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %f, %f, '%s', '%s', '%s', '%s')"
                    % ( lender_id, addressId,  row[13], row[10], row[11], row[12], row[0], row[1], row[3], row[4], row[5], row[6], row[7], row[8], row[9] ))
            insCur.execute("INSERT INTO dw_staging.person_business_addresses (address_id, addressable_type, business_person_id, address_type)"+\
                   " VALUES(%d,'%s',%d,'%s')" % ( addressId, 'Lenders', lender_id, 'LenderContact' ));
        else:
            insCur.execute("UPDATE dw_staging.lenders SET address_id=%d, contact_fax='%s', contact_first_name='%s', contact_last_name='%s', contact_phone='%s',credit_score_provider='%s', identifier='%s', manual_max=%f, manual_min=%f, name='%s', name_short ='%s', type='%s', updated_at='%s' WHERE id=%d VALUES ( %d, '%s', '%s', '%s', '%s', '%s', '%s', %f, %f, '%s', '%s', '%s', '%s', %d)"
                    % (addressId,  row[13], row[10], row[11], row[12], row[1], row[3], row[4], row[5], row[6], row[7], row[8], row[9], lender_id ))
    runLog("%d records processed." % cnt)
    MyDBConn.commit()

def loadLoansFromSource(MyDBConn, updatedAt):
    runLog("Loading data from loans.")
    if updatedAt is not None:
        selectSQL="SELECT active_items, admin_id, agency, amount, amount_requested, api_assisted, assigned_date, assignment_read_at, campaign_id, "+\
        "created_at, external_member_status, fees, fees_hash, handed_off_at, id, intended_use_of_funds, interest_rate, interest_rate_with_fees, "+ \
        "lead_id, lender_id, max_loan_amount_clean, medium, monthly_payment, partner_customer_id, partner_id, partner_referral_pct,"+ \
        "user_id, position, previous_state, prime_rate, priority, product_id, promotion_id, promo_code, recommended_apply_date, reengagement, referred_by_id, "+ \
        "sales_assisted, sales_assisted_denied_at, sales_assisted_requested_at,  source, state, term, updated_at  FROM dw_source.loans WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT active_items, admin_id, agency, amount, amount_requested, api_assisted, assigned_date, assignment_read_at, campaign_id, "+\
        "created_at, external_member_status, fees, fees_hash, handed_off_at, id, intended_use_of_funds, interest_rate, interest_rate_with_fees, "+ \
        "lead_id, lender_id, max_loan_amount_clean, medium, monthly_payment, partner_customer_id, partner_id, partner_referral_pct,"+ \
        "user_id, position, previous_state, prime_rate, priority, product_id, promotion_id, promo_code, recommended_apply_date, reengagement, referred_by_id, "+ \
        "sales_assisted, sales_assisted_denied_at, sales_assisted_requested_at,  source, state, term, updated_at  FROM dw_source.loans"
    personAdminSQL="SELECT id FROM dw_staging.persons WHERE id_from_source=%s AND source_table = '%s'"
    cur = MyDBConn.cursor(dictionary=True)
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        #print("Loan Id :%d" % row["id"])
        cnt = cnt + 1
        active_items=row["active_items"]
        if active_items is not None:
            active_items=active_items.replace("'","''")
        promo_code=row["promo_code"]
        if promo_code is not None:
            promo_code=promo_code.replace("'","''")
        personId=commonUtility.getSingleValFromDB( MyDBConn, personAdminSQL % (row["user_id"], 'users'))
        adminId=None
        if row["admin_id"] is not None:
            adminId=commonUtility.getSingleValFromDB( MyDBConn, personAdminSQL % (row["admin_id"], 'admins'))
        if personId is not None:
            lender_id=row["lender_id"]
            #"VALUES ('%s', %d, '%s', %, %d, %d, '%s', %s', '%s', '%s', '%s', %f, '%s',  '%s', %d, '%s', %f, %f, %d, %d,  %d,  '%s', %f, '%s', %d, %f, %d, %d, '%s', %f, %d, %d, %d, '%s', '%s', %d, %d, %d, '%s', '%s', '%s','%s', %d, '%s')"
            try:
                commonUtility.executeDBUpdateCmd(MyDBConn, "UPDATE dw_staging.loans SET rec_status=0 WHERE loan_id=%d AND rec_status=1" % row["id"] )
                insCur.execute("INSERT INTO dw_staging.loans (active_items, admin_id, agency, amount, amount_requested, api_assisted, assigned_date, assignment_read_at, campaign_id, "+
                "created_at, external_member_status, fees, fees_hash, handed_off_at, loan_id, intended_use_of_funds, interest_rate, interest_rate_with_fees, "+
                "lead_id, lender_id, max_loan_amount_clean, medium, monthly_payment, partner_customer_id, partner_id, partner_referral_pct,"+
                "person_id, position, previous_state, prime_rate, priority, product_id, promotion_id, promo_code, recommended_apply_date, reengagement, referred_by_id, "+
                "sales_assisted, sales_assisted_denied_at, sales_assisted_requested_at, source, state, term, updated_at ) " +\
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',  '%s', '%s', '%s', '%s', '%s', '%s', '%s',  '%s',  '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', %s, '%s')"
                % ( active_items, adminId, row["agency"], row["amount"], row["amount_requested"], row["api_assisted"], row["assigned_date"], row["assignment_read_at"], row["campaign_id"], row["created_at"], row["external_member_status"],
                   row["fees"], row["fees_hash"], row["handed_off_at"], row["id"], row["intended_use_of_funds"], row["interest_rate"], row["interest_rate_with_fees"] ,
                   row["lead_id"], row["lender_id"], row["max_loan_amount_clean"], row["medium"], row["monthly_payment"], row["partner_customer_id"], row["partner_id"], row["partner_referral_pct"],
                    personId, row["position"], row["previous_state"], row["prime_rate"], row["priority"], row["product_id"], row["promotion_id"], promo_code,row["recommended_apply_date"], row["reengagement"], row["referred_by_id"],
                    row["sales_assisted"], row["sales_assisted_denied_at"], row["sales_assisted_requested_at"], row["source"], row["state"] , row["term"], row["updated_at"]))
            except mysql.connector.Error as err:
                print("Loan Id :%d" % row["id"])
                print("Exception: {}".format(err))
                break
        else:
            runLog("Couldn't get address. Source id is %d" % row["user_id"] )
    runLog("%d records inserted." % cnt)
    MyDBConn.commit()

def loadAnswersFromSource(MyDBConn, updatedAt):
    runLog("Loading data from answers.")
    if updatedAt is not None:
        selectSQL="SELECT id, answerable_id, answerable_type, created_at, question_id, type, updated_at, value  FROM dw_source.answers WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT id, answerable_id, answerable_type, created_at, question_id, type, updated_at, value  FROM dw_source.answers"
    cur = MyDBConn.cursor(dictionary=True)
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        answerable_type=row["answerable_type"]
        if answerable_type == "Guarantor":
            answerable_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.persons WHERE id_from_source=%d AND source_table='guarantors'" %  ( row["answerable_id"] ) )
        else:
            answerable_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.businesses WHERE id_from_source=%d AND source_table='businesses'" %  ( row["answerable_id"] ) )
        if answerable_id is not None:
            answer_value=row["value"]
            if answer_value is not None:
                answer_value=answer_value.replace("'","''")
            cnt = cnt + 1
            insORupdate="I"
            if updatedAt is not None:
                AnswerId=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.answers WHERE id=%d" %  ( row["id"]) )
                if AnswerId is not None:
                    insORupdate='U'
            if insORupdate == "I":
                #print("Inserting Id :%d :: %s" % (row["id"], answerable_type) )
                insCur.execute("INSERT INTO dw_staging.answers (id, answerable_id, answerable_type, created_at, question_id, type, updated_at, value) VALUES (%d, %d, '%s', '%s', %d, '%s', '%s', '%s')"
                        % ( row["id"], answerable_id, row["answerable_type"], row["created_at"], row["question_id"], row["type"], row["updated_at"], answer_value ))
            else:
                #print("Updating :%d :: %s" % (row["id"], answerable_type) )
                insCur.execute("UPDATE dw_staging.answers SET answerable_id=%d, answerable_type='%s', question_id=%d, type='%s', updated_at='%s', value='%s' WHERE id=%d"
                        % ( answerable_id, row["answerable_type"], row["question_id"], row["type"], row["updated_at"], answer_value, row["id"]))
        #else:
        #    print("Wrong record Id :%d :: %s" % (row["id"], answerable_type) )

    runLog("%d records inserted." % cnt)
    MyDBConn.commit()

def loadFinancial_AdjFromSource(MyDBConn, updatedAt):
    runLog("Loading data from financial_adjustments.")
    if updatedAt is not None:
        selectSQL="SELECT adjustable_id, adjustable_type, category, created_at, data, description,id, reason, type, updated_at  FROM dw_source.financial_adjustments WHERE updated_at > '%s'" % updatedAt
    else:
        selectSQL="SELECT adjustable_id, adjustable_type, category, created_at, data, description, id, reason, type, updated_at  FROM dw_source.financial_adjustments"
    cur = MyDBConn.cursor(dictionary=True)
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        adjustable_type=row["adjustable_type"]
        if adjustable_type == "Guarantor":
            adjustable_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.persons WHERE id_from_source=%d AND source_table='guarantors'" %  ( row["adjustable_id"] ) )
        else:
            adjustable_id=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.businesses WHERE id_from_source=%d AND source_table='businesses'" %  ( row["adjustable_id"] ) )
        if adjustable_id is not None:
            Data=row["data"]
            if Data is not None:
                Data=Data.replace("'","''")
            Reason=row["reason"]
            if Reason is not None:
                Reason=Reason.replace("'","''")

            Desc=row["description"]
            if Desc is not None:
                Desc=Desc.replace("'","''")
            cnt = cnt + 1
            insORupdate="I"
            if updatedAt is not None:
                AdjId=commonUtility.getSingleValFromDB(MyDBConn, "SELECT id FROM dw_staging.financial_adjustments WHERE id=%d" %  ( row["id"] ) )
                if AdjId is not None:
                    insORupdate='U'
            if insORupdate == "I":
                #print("Inserting Id :%d :: %s" % (row["id"], adjustable_type) )
                insCur.execute("INSERT INTO dw_staging.financial_adjustments (id, adjustable_id, adjustable_type, category, created_at, data, description, reason, type, updated_at) VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s','%s','%s')"
                        % ( row["id"], adjustable_id, row["adjustable_type"], row["category"], row["created_at"], Data, Desc, Reason, row["type"], row["updated_at"]))
            else:
                #print("Updating :%d :: %s" % (row["id"], adjustable_type) )
                insCur.execute("UPDATE dw_staging.financial_adjustments SET adjustable_id=%d, adjustable_type='%s', category='%s', data='%s', description='%s', reason='%s', type='%s', updated_at='%s' WHERE id=%d"
                        % ( adjustable_id, row["adjustable_type"], row["category"], Data, Desc, Reason, row["type"], row["updated_at"], row["id"]))
        #else:
        #    print("Wrong record Id :%d :: %s" % (row["id"], adjustable_type) )

    runLog("%d records inserted." % cnt)
    MyDBConn.commit()

def loadDecisionsFromSource(MyDBConn, updatedAt):
    selectSQL="SELECT amount,business_score,business_type,created_at,decision,guarantors_20,id,lender_id,liquidity_ratio,liquid_credit_id,loan_id,max_amount,minimum_credit_score,"+ \
    "mitigating_factor,product_id,request_type,risk_rating,risk_rating_data,risk_rating_v2,smart_rate,smart_rate_v2,updated_at  FROM dw_source.decisions"
    cur = MyDBConn.cursor(dictionary=True)
    insCur = MyDBConn.cursor()
    cur.execute(selectSQL)
    rows = cur.fetchall()
    cnt=0
    columns=' '
    ColValues= ' '
    tableName=' '
    for row in rows:
        print("Decision Id :%d" % row["id"])
        risk_rating_data=row["risk_rating_data"]
        if risk_rating_data is not None:
            risk_rating_data=risk_rating_data.replace("'","''")
        cnt = cnt + 1
        insCur.execute("INSERT INTO dw_staging.decisions(amount,business_score,business_type,created_at,decision,guarantors_20,id,lender_id,liquidity_ratio,liquid_credit_id,loan_id,max_amount,minimum_credit_score,mitigating_factor,product_id,request_type,risk_rating,risk_rating_data,risk_rating_v2,smart_rate,smart_rate_v2,updated_at) "+\
                       " VALUES( '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
                       % (row["amount"],row["business_score"],row["business_type"],row["created_at"],row["decision"],row["guarantors_20"],row["id"],row["lender_id"],row["liquidity_ratio"],row["liquid_credit_id"],row["loan_id"],row["max_amount"],row["minimum_credit_score"],row["mitigating_factor"],row["product_id"],row["request_type"],row["risk_rating"],risk_rating_data,row["risk_rating_v2"],row["smart_rate"],row["smart_rate_v2"],row["updated_at"]))
    runLog("%d records inserted." % cnt)
    MyDBConn.commit()

def Main():
    MyDBConn=MySQLConn()
    insCur = MyDBConn.cursor()
    updatedAt=commonUtility.getSingleValFromDB(MyDBConn, "SELECT last_process_ts FROM dw_staging.dw_processes_info WHERE process_name= 'LoadFromSmartBizApp' AND id= (SELECT MAX(id) FROM dw_staging.dw_processes_info)")
    print(updatedAt)
    insCur.execute("INSERT INTO dw_staging.dw_processes_info (process_name) VALUES('LoadFromSmartBizApp')" )
    #create_insert_stmts(MyDBConn)
    loadUsersFromSource(MyDBConn, updatedAt)
    loadAdminsFromSource(MyDBConn, updatedAt)
    loadGuarantorsFromSource(MyDBConn, updatedAt)
    loadLendersFromSource(MyDBConn, updatedAt)
    loadLoansFromSource(MyDBConn, updatedAt)
    loadBusinessesFromSource(MyDBConn, updatedAt)
    loadAnswersFromSource(MyDBConn, updatedAt)
    loadFinancial_AdjFromSource(MyDBConn, updatedAt)
    #loadDecisionsFromSource(MyDBConn)

if __name__ == '__main__':
    Main()