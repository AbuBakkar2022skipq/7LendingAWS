import requests as req
import sys
import logging
import pymysql
import datetime
import statistics
import heapq
from random import randint

def lambda_handler(event, context):
    rds_host = "sevenlendingdb.cvnlc8wxkgyn.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "123qweQWE"
    db_name = "N7Lending"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    # Logic Code Starts Here

    client_id = '16p7n5khh0hvmb2146mj8iggoc'
    client_secret = 'cv9djs2b2s85bp2t4f2ummcn5nhm0l2dmrjq0ilvsm3jod2sf6s'

    token_url = 'https://authenticate.constellation1apis.com/oauth2/token'

    d = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}

    r = req.post(token_url, data=d).json()

    access_token = r['access_token']
    header = 'Bearer ' + access_token
    hz = {'Authorization': header}
    
    one_YearAgo_Today = datetime.datetime.now() - datetime.timedelta(days=365)
    z_ = str(one_YearAgo_Today.strftime('%Y-%m-%d')) + "T" + "00:00:00" + "Z"

    top_=str(1)
    url2_ = 'https://listings.constellation1apis.com/OData/Property?$top=' + top_ + '&$ignorenulls=true&$filter=OnMarketTimestamp%20ge%20' + z_ + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp'
    url2_pikes_ = 'https://listings.constellation1apis.com/OData/Property?$top=' + top_ + '&$ignorenulls=true&$filter=OnMarketTimestamp%20ge%20' + z_ +'%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp'


    url_ = 'https://listings.constellation1apis.com/OData/Property?$top=' + top_ + '&$ignorenulls=true&$filter=OnMarketTimestamp%20ge%20' + z_ + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Active%27&$select=PostalCode'
    url_pikes_ = 'https://listings.constellation1apis.com/OData/Property?$top=' + top_ + '&$ignorenulls=true&$filter=OnMarketTimestamp%20ge%20' + z_ + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Active%27&$select=PostalCode'

    response2_ = req.get(url2_, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties
    response2_pikes_ = req.get(url2_pikes_, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties
    
    response_ = req.get(url_, headers=hz, timeout=60, stream=True).json()  # Get Active Properties
    response_pikes_ = req.get(url_pikes_, headers=hz, timeout=60, stream=True).json()  # Get Active Properties
    
    total_units_sold_ = int(response2_['@odata.totalCount']) + int(response2_pikes_['@odata.totalCount'])
    total_units_open_ = int(response_['@odata.totalCount']) + int(response_pikes_['@odata.totalCount'])
    
    t1 = str(one_YearAgo_Today.strftime('%Y-%m-%d'))
    t = datetime.datetime.now()
    t2 = str(t.strftime('%Y-%m-%d'))
    time_period = "From " + str(t1) + ' To ' + str(t2)
    
    with conn.cursor() as cur:
        cur.execute("DELETE FROM raw_data_open_properties")
        cur.execute("DELETE FROM raw_data_closed_properties")
    conn.commit()
    
    prices = [0]
    dictionary = {}
    postal_codes = {}
    
    
    for d in range(366):
        oneYearAgoToday = datetime.datetime.now() - datetime.timedelta(days=d)
        one_day_later = datetime.datetime.now() - datetime.timedelta(days=(d - 1))
        t = datetime.datetime.now()
        today = str(t.strftime('%Y-%m-%d')) + "T" + "00:00:00" + "Z"

        z = str(oneYearAgoToday.strftime('%Y-%m-%d')) + "T" + "00:00:00" + "Z"
        zg = str(one_day_later.strftime('%Y-%m-%d')) + "T" + "00:00:00" + "Z"

        top = str(500000)

        query = 'OnMarketTimestamp,ListPrice,PostalCode,OriginatingSystemName,ListAgentEmail,ListAgentFullName,ListAgentPreferredPhone,StandardStatus,ListingId'
        
        url = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=OnMarketTimestamp%20gt%20' + z + '%20and%20OnMarketTimestamp%20le%20' + zg + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

        url2 = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=OnMarketTimestamp%20gt%20' + z + '%20and%20OnMarketTimestamp%20le%20' + zg + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp,' + query

        url_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=OnMarketTimestamp%20gt%20' + z + '%20and%20OnMarketTimestamp%20le%20' + zg + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

        url2_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=OnMarketTimestamp%20gt%20' + z + '%20and%20OnMarketTimestamp%20le%20' + zg + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp,' + query

        

        response = req.get(url, headers=hz, timeout=60, stream=True).json()  # Get Active Properties

        response2 = req.get(url2, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties

        response_pikes = req.get(url_pikes, headers=hz, timeout=60, stream=True).json()  # Get Active Properties

        response2_pikes = req.get(url2_pikes, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties

        # Logic Code Ends Here

        # Declaration Of Variables Starts Here
        open_response_colorado = response['value']
        #l_id = 'NULL'
        l_status = 'NULL'
        l_postal_code = 'NULL'
        l_realtor_name = 'NULL'
        l_listing_price = 'NULL'
        l_listing_date = 'NULL'

        closed_response_colorado = response2['value']
        #l2_id = 'NULL'
        l2_status = 'NULL'
        l2_postal_code = 'NULL'
        l2_realtor_name = 'NULL'
        l2_listing_price = 'NULL'
        l2_listing_date = 'NULL'
        l2_closing_date = 'NULL'

        open_response_pikes = response_pikes['value']
        #p_id = 'NULL'
        p_status = 'NULL'
        p_postal_code = 'NULL'
        p_realtor_name = 'NULL'
        p_listing_price = 'NULL'
        p_listing_date = 'NULL'

        closed_response_pikes = response2_pikes['value']
        #p2_id = 'NULL'
        p2_status = 'NULL'
        p2_postal_code = 'NULL'
        p2_realtor_name = 'NULL'
        p2_listing_price = 'NULL'
        p2_listing_date = 'NULL'
        p2_closing_date = 'NULL'

        # total_open_properties = int(response['@odata.totalCount']) + int(response_pikes['@odata.totalCount'])
        # total_closed_properties = int(response2['@odata.totalCount']) + int(response2_pikes['@odata.totalCount'])

        # Declaration Of Variables Ends Here
        with conn.cursor() as cur:
            # cur.execute("create table results (date_inserted varchar(255) NOT NULL, time_period varchar(255), average_price varchar(255), median_price varchar(255), total_units_sold varchar(255), postal_code_1 varchar(255), postal_code_2 varchar(255), postal_code_3 varchar(255), postal_code_4 varchar(255), postal_code_5 varchar(255), realtor_1 varchar(255), realtor_2 varchar(255), realtor_3 varchar(255), realtor_4 varchar(255), realtor_5 varchar(255), PRIMARY KEY (date_inserted))")
            # cur.execute("create table raw_data_open_properties (ListingId varchar(255) not NULL, status varchar(255), postal_code varchar(255), realtor_name varchar(255), listing_price varchar(255), total_open_properties varchar(255), Listing_Date varchar(255), PRIMARY KEY (ListingId))")
            # cur.execute("create table raw_data_closed_properties (ListingId varchar(255) not NULL, status varchar(255), postal_code varchar(255), realtor_name varchar(255), listing_price varchar(255), total_closed_properties varchar(255), Listing_Date varchar(255),  Selling_Date varchar(255),  PRIMARY KEY (ListingId))")
            ins = 'insert ignore into results (date_inserted, time_period, average_price, median_price, total_units_sold, postal_code_1, postal_code_2, postal_code_3, postal_code_4, postal_code_5, realtor_1, realtor_2, realtor_3, realtor_4, realtor_5) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            ins_open = 'insert ignore into raw_data_open_properties (ListingId, status, postal_code, realtor_name, listing_price, total_open_properties, Listing_Date) values(%s,%s,%s,%s,%s,%s,%s)'
            ins_closed = 'insert ignore into raw_data_closed_properties (ListingId, status, postal_code, realtor_name, listing_price, total_closed_properties, Listing_Date, Selling_Date) values(%s,%s,%s,%s,%s,%s,%s,%s)'

            # cur.execute("DELETE FROM raw_data_open_properties")
            # cur.execute("DELETE FROM raw_data_closed_properties")

            for i in range(len(open_response_colorado)):
                try:
                    # for open properties in ReColorado
                    l_id = open_response_colorado[i]['ListingId']
                    if 'StandardStatus' in open_response_colorado[i]:
                        l_status = open_response_colorado[i]['StandardStatus']
                    if 'PostalCode' in open_response_colorado[i]:    
                        l_postal_code = open_response_colorado[i]['PostalCode']
                        postal=open_response_colorado[i]['PostalCode']
                        if postal not in postal_codes:
                            postal_codes[postal] = 1
                        elif postal in postal_codes:
                            postal_codes[postal] += 1
                    if 'ListAgentFullName' in open_response_colorado[i]:    
                        l_realtor_name = open_response_colorado[i]['ListAgentFullName']
                        agent=open_response_colorado[i]['ListAgentFullName']
                        if agent not in dictionary:
                            dictionary[agent] = 1
                        elif agent in dictionary:
                            dictionary[agent] += 1
                    if 'ListPrice' in open_response_colorado[i]:
                        l_listing_price = open_response_colorado[i]['ListPrice']
                        prices.append(int(open_response_colorado[i]['ListPrice']))
                    if 'OnMarketTimestamp' in open_response_colorado[i]:
                        l_listing_date = open_response_colorado[i]['OnMarketTimestamp']
                    cur.execute(ins_open, ((str(l_id)), str(l_status), str(l_postal_code), str(l_realtor_name),str(l_listing_price), str(total_units_open_), str(l_listing_date)))
                    l_id = 'NULL'
                    l_status = 'NULL'
                    l_postal_code = 'NULL'
                    l_realtor_name = 'NULL'
                    l_listing_price = 'NULL'
                    l_listing_date = 'NULL'

                except KeyError:
                    print('key error when Entering')
                    continue
            for i in range(len(open_response_pikes)):
                try:
                    # for open properties in PikesPeak
                    p_id = open_response_pikes[i]['ListingId']
                    if 'StandardStatus' in open_response_pikes[i]:
                        p_status = open_response_pikes[i]['StandardStatus']
                    if 'PostalCode' in open_response_pikes[i]:
                        p_postal_code = open_response_pikes[i]['PostalCode']
                        postal=open_response_pikes[i]['PostalCode']
                        if postal not in postal_codes:
                            postal_codes[postal] = 1
                        elif postal in postal_codes:
                            postal_codes[postal] += 1
                    if 'ListAgentFullName' in open_response_pikes[i]:
                        p_realtor_name = open_response_pikes[i]['ListAgentFullName']
                        agent=open_response_pikes[i]['ListAgentFullName']
                        if agent not in dictionary:
                            dictionary[agent] = 1
                        elif agent in dictionary:
                            dictionary[agent] += 1
                    if 'ListPrice' in open_response_pikes[i]:
                        p_listing_price = open_response_pikes[i]['ListPrice']
                        prices.append(int(open_response_pikes[i]['ListPrice']))
                    if 'OnMarketTimestamp' in open_response_pikes[i]:
                        p_listing_date = open_response_pikes[i]['OnMarketTimestamp']
                    cur.execute(ins_open, ((str(p_id)), str(p_status), str(p_postal_code), str(p_realtor_name),str(p_listing_price), str(total_units_open_), str(p_listing_date)))
                    p_status = 'NULL'
                    p_postal_code = 'NULL'
                    p_realtor_name = 'NULL'
                    p_listing_price = 'NULL'
                    p_listing_date = 'NULL'
            

                except KeyError:
                    print('key error when Etering')
                    continue
            for i in range(len(closed_response_pikes)):
                try:
                    # for closed properties in PikesPeak
                    p2_id = closed_response_pikes[i]['ListingId']
                    if 'StandardStatus' in closed_response_pikes[i]:
                        p2_status = closed_response_pikes[i]['StandardStatus']
                    if 'PostalCode' in closed_response_pikes[i]:
                        p2_postal_code = closed_response_pikes[i]['PostalCode']
                        postal=closed_response_pikes[i]['PostalCode']
                        if postal not in postal_codes:
                            postal_codes[postal] = 1
                        elif postal in postal_codes:
                            postal_codes[postal] += 1
                    if 'ListAgentFullName' in closed_response_pikes[i]:
                        p2_realtor_name = closed_response_pikes[i]['ListAgentFullName']
                        agent=closed_response_pikes[i]['ListAgentFullName']
                        if agent not in dictionary:
                            dictionary[agent] = 1
                        elif agent in dictionary:
                            dictionary[agent] += 1
                    if 'ListPrice' in closed_response_pikes[i]:
                        p2_listing_price = closed_response_pikes[i]['ListPrice']
                        prices.append(int(closed_response_pikes[i]['ListPrice']))
                    if 'OnMarketTimestamp' in closed_response_pikes[i]:
                        p2_listing_date = closed_response_pikes[i]['OnMarketTimestamp']
                    if 'OffMarketTimestamp' in closed_response_pikes[i]:
                        p2_closing_date = closed_response_pikes[i]['OffMarketTimestamp']
                    cur.execute(ins_closed, ((str(p2_id)), str(p2_status), str(p2_postal_code), str(p2_realtor_name),str(p2_listing_price), str(total_units_sold_), str(p2_listing_date),str(p2_closing_date)))
                    p2_status = 'NULL'
                    p2_postal_code = 'NULL'
                    p2_realtor_name = 'NULL'
                    p2_listing_price = 'NULL'
                    p2_listing_date = 'NULL'
                    p2_closing_date = 'NULL'
                except KeyError:
                    print('key error when Entering')
                    continue
            for i in range(len(closed_response_colorado)):
                try:
                    # for closed properties in ReColorado
                    l2_id = closed_response_colorado[i]['ListingId']
                    if 'StandardStatus' in closed_response_colorado[i]:
                        l2_status = closed_response_colorado[i]['StandardStatus']
                    if 'PostalCode' in closed_response_colorado[i]:
                        l2_postal_code = closed_response_colorado[i]['PostalCode']
                        postal=closed_response_colorado[i]['PostalCode']
                        if postal not in postal_codes:
                            postal_codes[postal] = 1
                        elif postal in postal_codes:
                            postal_codes[postal] += 1
                    if 'ListAgentFullName' in closed_response_colorado[i]:
                        l2_realtor_name = closed_response_colorado[i]['ListAgentFullName']
                        agent=closed_response_colorado[i]['ListAgentFullName']
                        if agent not in dictionary:
                            dictionary[agent] = 1
                        elif agent in dictionary:
                            dictionary[agent] += 1
                    if 'ListPrice' in closed_response_colorado[i]:
                        l2_listing_price = closed_response_colorado[i]['ListPrice']
                        prices.append(int(closed_response_colorado[i]['ListPrice']))
                    if 'OnMarketTimestamp' in closed_response_colorado[i]:
                        l2_listing_date = closed_response_colorado[i]['OnMarketTimestamp']
                    if 'OffMarketTimestamp' in closed_response_colorado[i]:
                        l2_closing_date = closed_response_colorado[i]['OffMarketTimestamp']
                    cur.execute(ins_closed, ((str(l2_id)), str(l2_status), str(l2_postal_code), str(l2_realtor_name), str(l2_listing_price), str(total_units_sold_), str(l2_listing_date), str(l2_closing_date)))
                    
                    l2_status = 'NULL'
                    l2_postal_code = 'NULL'
                    l2_realtor_name = 'NULL'
                    l2_listing_price = 'NULL'
                    l2_listing_date = 'NULL'
                    l2_closing_date = 'NULL'
                    

                    print('Value Validated')
                except KeyError:
                    print('key error When Entering')
                    continue
                # ListingId, status, postal_code, realtor_name, listing_price, total_open_properties

            conn.commit()


    
    average = sum(prices)/len(prices)
    postal_5 = heapq.nlargest(5, postal_codes, key=postal_codes.get)
    realtors_5 = heapq.nlargest(5, dictionary, key=dictionary.get)
    median = statistics.median(prices)
    units_sold = total_units_sold_
    # average, median, realtors, total_units_sold, postal, today
    with conn.cursor() as cur:
        cur.execute(ins, (str(t), str(average), str(time_period), str(median), str(units_sold), str(postal_5[0]), str(postal_5[1]), str(postal_5[2]), str(postal_5[3]), str(postal_5[4]), str(realtors_5[0]), str(realtors_5[1]), str(realtors_5[2]), str(realtors_5[3]), str(realtors_5[4])))
    conn.commit()
    # print(str(response['data']['report'][len(response['data']['report'])-1]))

    return 'complete'