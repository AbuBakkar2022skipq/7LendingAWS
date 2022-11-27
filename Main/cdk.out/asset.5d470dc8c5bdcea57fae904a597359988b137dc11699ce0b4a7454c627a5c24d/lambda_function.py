import requests as req
import sys
import logging
import pymysql


    
def lambda_handler(event, context):
    
    url = 'https://app18.workamajig.com/api/beta1/reports?reportkey=akV4U3A3WGw0bWJmUW9ybm5zbkdzQT090'
    hz={'APIAccessToken': 'd2a7/5zhBsBcjSLEzCaE0v7zbUT8zjOpLXQCveUQWsyT+CyhiwoshPoCai1EZh4dC40+QfLLYprLPtPxFZxnjQ==', 'UserToken': 'rQ4uAo1EXDYe0dCM5xqNHGLVmKRGmucjBR5hrfQtWDT6CuYMZGj2EDtB7SGhX12YAwhBFOrLP6ZUGestEB2IVQ2'}
    response = req.get(url, headers=hz, timeout = 60).json()
    
    
    rds_host  = "wmjproddb.cxu4yjxbpose.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "123qweQWE"
    db_name = "wmjProd"
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    try:
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    
    item_count = 0

    with conn.cursor() as cur:
        #cur.execute("create table records ( record_ID int NOT NULL AUTO_INCREMENT, parent_Account_Number varchar(255), transaction_Amount varchar(255), gL_Account_Name_Full varchar(255), transaction_Memo varchar(255),gL_Account_Name varchar(255), debit_Amount varchar(255), date_Posted varchar(255),account_Type varchar(255), credit_Amount varchar(255),PRIMARY KEY (record_ID))")
        for i in range(len(response['data']['report'])):
            ins= 'insert into records (record_ID,parent_Account_Number,transaction_Amount,gL_Account_Name_Full,transaction_Memo,gL_Account_Name,debit_Amount,date_Posted,account_Type,credit_Amount) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            
            pan=f"""{str(response['data']['report'][i]['parent_Account_Number'])}"""
            t_amm=f"""{str(response['data']['report'][i]['transaction_Amount'])}"""
            acc_n_full=f"""{str(response['data']['report'][i]['gL_Account_Name_Full'])}"""
            t_memo=f"""{str(response['data']['report'][i]['transaction_Memo'])}"""
            acc_n=f"""{str(response['data']['report'][i]['gL_Account_Name'])}"""
            deb_amm=f"""{str(response['data']['report'][i]['debit_Amount'])}"""
            d_posted=f"""{str(response['data']['report'][i]['date_Posted'])}"""
            acc_type=f"""{str(response['data']['report'][i]['account_Type'])}"""
            cred_amm=f"""{str(response['data']['report'][i]['credit_Amount'])}"""
            
            cur.execute(ins, (None, pan, t_amm, acc_n_full, t_memo, acc_n, deb_amm, d_posted, acc_type, cred_amm))
        conn.commit()

        
    #print(str(response['data']['report'][len(response['data']['report'])-1]))
    
    return "Complete"
