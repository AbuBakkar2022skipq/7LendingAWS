import requests as req
import sys
import logging
import pymysql


    
def lambda_handler(event, context):
    rds_host  = "wmjdb1.cxu4yjxbpose.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "123qweQWE"
    db_name = "wmjdb1"
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    try:
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    #url = 'https://app18.workamajig.com/api/beta1/reports?reportkey=akV4U3A3WGw0bWJmUW9ybm5zbkdzQT090'
    #response = req.get(url, headers={        'APIAccessToken': 'd2a7/5zhBsBcjSLEzCaE0v7zbUT8zjOpLXQCveUQWsyT+CyhiwoshPoCai1EZh4dC40+QfLLYprLPtPxFZxnjQ==',        'UserToken': 'rQ4uAo1EXDYe0dCM5xqNHGLVmKRGmucjBR5hrfQtWDT6CuYMZGj2EDtB7SGhX12YAwhBFOrLP6ZUGestEB2IVQ2'}, timeout = 60).json()
    
    
    item_count = 0

    with conn.cursor() as cur:
        #cur.execute("create table Employee ( EmpID  int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))")
        #cur.execute('insert into Employee (EmpID, Name) values(1, "Joe")')
        #cur.execute('insert into Employee (EmpID, Name) values(2, "Bob")')
        #cur.execute('insert into Employee (EmpID, Name) values(3, "Mary")')
        conn.commit()
        cur.execute("select * from Employee")
        #cur.execute("TRUNCATE TABLE wmjdb1")

        cur.execute("DELETE FROM Table_name WHERE firstname='Joe'")
        for row in cur:
            item_count += 1
            logger.info(row)
            print(row)
    #print(str(response['data']['report'][0]))
    
    return "Added %d items from RDS MySQL table" %(item_count)
