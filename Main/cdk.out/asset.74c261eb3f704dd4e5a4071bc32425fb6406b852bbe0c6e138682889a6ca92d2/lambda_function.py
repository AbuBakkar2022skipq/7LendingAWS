import requests as req
import sys
import logging
import pymysql
import datetime
import statistics
import heapq

    
def lambda_handler(event, context):
    
    rds_host  = "sevenlendingdb.cvnlc8wxkgyn.us-east-2.rds.amazonaws.com"
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
    
    #Logic Code Starts Here


    client_id = '16p7n5khh0hvmb2146mj8iggoc'
    client_secret = 'cv9djs2b2s85bp2t4f2ummcn5nhm0l2dmrjq0ilvsm3jod2sf6s'

    token_url = 'https://authenticate.constellation1apis.com/oauth2/token'

    d = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}

    r = req.post(token_url, data=d).json()

    access_token = r['access_token']

    oneYearAgoToday = datetime.datetime.now() - datetime.timedelta(days=360)
    today=datetime.datetime.now()
    z = str(oneYearAgoToday.strftime('%Y-%m-%d')) + "T" + "00:00:00" + "Z"
    top = str(500000)
    query='OnMarketTimestamp,ListPrice,PostalCode,OriginatingSystemName,ListAgentEmail,ListAgentFullName,ListAgentPreferredPhone,StandardStatus,ListingId, '

    url = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

    url2 = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp,' + query

    url_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

    url2_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=OffMarketTimestamp,' + query

    header = 'Bearer ' + access_token

    hz = {'Authorization': header}

    response = req.get(url, headers=hz, timeout=60, stream=True).json()  # Get Active Properties

    response2 = req.get(url2, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties

    response_pikes = req.get(url_pikes, headers=hz, timeout=60, stream=True).json()  # Get Active Properties

    response2_pikes = req.get(url2_pikes, headers=hz, timeout=60, stream=True).json()  # Get Closed Properties

    total_units_sold = int(response2['@odata.totalCount']) + int(response2_pikes['@odata.totalCount'])

    
    dictionary = {}

    prices = []
    
    result = response['value']
    result_pikes = response_pikes['value']
    
    for i in range(len(result)):
        try:
            agent_name_pikes = result_pikes[i]['ListAgentFullName']
            agent_name_coldo = result[i]['ListAgentFullName']
            if agent_name_coldo not in dictionary:
                dictionary[agent_name_coldo] = 1

            elif agent_name_coldo in dictionary:
                dictionary[agent_name_coldo] += 1

            if agent_name_pikes not in dictionary:
                dictionary[agent_name_pikes] = 1
            elif agent_name_pikes in dictionary:
                dictionary[agent_name_pikes] += 1

            if i < len(result):
                prices.append(result[i]['ListPrice'])

            if i < len(result_pikes):
                prices.append(result_pikes[i]['ListPrice'])

        except KeyError:
            print('key error')
            continue
        except IndexError:
            break

    n2 = response2['value']
    postal_codes = {}

    for j in range(len(n2)):
        try:
            postal_p = result_pikes[j]['PostalCode']
            postal_r = result[j]['PostalCode']
            if postal_r not in postal_codes:
                postal_codes[postal_r] = 1

            elif postal_r in postal_codes:
                postal_codes[postal_r] += 1

            if postal_p not in postal_codes:
                postal_codes[postal_p] = 1

            elif postal_p in postal_codes:
                postal_codes[postal_p] += 1

        except KeyError:
            print('key error')
            continue
        except IndexError:
            break

    # result['ListAgentEmail']
    # result['ListAgentFullName']
    # result['ListPrice']
    # result['OriginatingSystemName']
    # result['PostalCode']

    postal = heapq.nlargest(5, postal_codes, key=postal_codes.get)
    realtors = heapq.nlargest(5, dictionary, key=dictionary.get)
    average = sum(prices) / len(prices)
    median = statistics.median(prices)
    time_period=str(oneYearAgoToday)+'-'+str(today)

    # average, median, realtors, total_units_sold, postal, today

    #Logic Code Ends Here

    #Declaration Of Variables Starts Here
    open_response_colorado=response['value']
    l_id='na'
    l_status='na'
    l_postal_code='na'
    l_realtor_name='na'
    l_listing_price='na'
    l_email='na'
    

    closed_response_colorado=response2['value']
    l2_id='na'
    l2_status='na'
    l2_postal_code='na'
    l2_realtor_name='na'
    l2_listing_price='na'
    l2_email='na'
    
    open_response_pikes=response_pikes['value']
    p_id='na'
    p_status='na'
    p_postal_code='na'
    p_realtor_name='na'
    p_listing_price='na'
    p_email='na'



    closed_response_pikes=response2_pikes['value']
    p2_id='na'
    p2_status='na'
    p2_postal_code='na'
    p2_realtor_name='na'
    p2_listing_price='na'
    p2_email='na'
    #status varchar(255), postal_code varchar(255), realtor_name varchar(255), listing_price
    
    total_open_properties=int(response['@odata.totalCount'])+int(response_pikes['@odata.totalCount'])
    total_closed_properties=int(response2['@odata.totalCount'])+int(response2_pikes['@odata.totalCount'])
    
    #Declaration Of Variables Ends Here
    with conn.cursor() as cur:
        #cur.execute("create table results (date_inserted varchar(255) NOT NULL, time_period varchar(255), average_price varchar(255), median_price varchar(255), total_units_sold varchar(255), postal_code_1 varchar(255), postal_code_2 varchar(255), postal_code_3 varchar(255), postal_code_4 varchar(255), postal_code_5 varchar(255), realtor_1 varchar(255), realtor_2 varchar(255), realtor_3 varchar(255), realtor_4 varchar(255), realtor_5 varchar(255), PRIMARY KEY (date_inserted))")
        #cur.execute("create table raw_data_open_properties (ListingId varchar(255) NOT NULL, status varchar(255), postal_code varchar(255), realtor_name varchar(255), listing_price varchar(255), total_open_properties varchar(255),  PRIMARY KEY (ListingId))")
        #cur.execute("create table raw_data_closed_properties (ListingId varchar(255) NOT NULL, status varchar(255), postal_code varchar(255), realtor_name varchar(255), listing_price varchar(255), total_open_properties varchar(255),  PRIMARY KEY (ListingId))")
        ins= 'insert into results (date_inserted, time_period, average_price, median_price, total_units_sold, postal_code_1, postal_code_2, postal_code_3, postal_code_4, postal_code_5, realtor_1, realtor_2, realtor_3, realtor_4, realtor_5) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        ins_open= 'insert into raw_data_open_properties (ListingId, status, postal_code, realtor_name, listing_price, total_open_properties) values(%s,%s,%s,%s,%s,%s)'
        ins_closed= 'insert into raw_data_closed_properties (ListingId, status, postal_code, realtor_name, listing_price, total_open_properties) values(%s,%s,%s,%s,%s,%s)'


        #cur.execute("DELETE FROM raw_data_open_properties")
        #cur.execute("DELETE FROM raw_data_closed_properties")

        for i in range(int(top)):
            try:
                #for open properties in ReColorado
                l_id=open_response_colorado[i]['ListingId']
                l_status=open_response_colorado[i]['StandardStatus']
                l_postal_code=open_response_colorado[i]['PostalCode']
                l_realtor_name=open_response_colorado[i]['ListAgentFullName']
                l_listing_price=open_response_colorado[i]['ListPrice']             

                #for open properties in PikesPeak
                p_id=open_response_pikes[i]['ListingId']
                p_status=open_response_pikes[i]['StandardStatus']
                p_postal_code=open_response_pikes[i]['PostalCode']
                p_realtor_name=open_response_pikes[i]['ListAgentFullName']
                p_listing_price=open_response_pikes[i]['ListPrice']             

                #for closed properties in PikesPeak
                p2_id=closed_response_pikes[i]['ListingId']
                p2_status=closed_response_pikes[i]['StandardStatus']
                p2_postal_code=closed_response_pikes[i]['PostalCode']
                p2_realtor_name=closed_response_pikes[i]['ListAgentFullName']
                p2_listing_price=closed_response_pikes[i]['ListPrice']

                #for closed properties in ReColorado
                l2_id=closed_response_colorado[i]['ListingId']
                l2_status=closed_response_colorado[i]['StandardStatus']
                l2_postal_code=closed_response_colorado[i]['PostalCode']
                l2_realtor_name=closed_response_colorado[i]['ListAgentFullName']
                l2_listing_price=closed_response_colorado[i]['ListPrice'] 

            except KeyError:
                print('key error')
                continue
            # ListingId, status, postal_code, realtor_name, listing_price, total_open_properties
            cur.execute(ins_open, (str(l_id), str(l_status), str(l_postal_code), str(l_realtor_name), str(l_listing_price), str(total_open_properties)))
            cur.execute(ins_open, (str(p_id), str(p_status), str(p_postal_code), str(p_realtor_name), str(p_listing_price), str(total_open_properties)))
            cur.execute(ins_closed, (str(p2_id), str(p2_status), str(p2_postal_code), str(p2_realtor_name), str(p2_listing_price), str(total_closed_properties)))
            cur.execute(ins_closed, (str(l2_id), str(l2_status), str(l2_postal_code), str(l2_realtor_name), str(l2_listing_price), str(total_closed_properties)))

        #cur.execute(ins, (str(today), str(time_period), str(average),str(median), str(total_units_sold), str(postal[0]), str(postal[1]), str(postal[2]), str(postal[3]), str(postal[4]), str(realtors[0]), str(realtors[1]), str(realtors[2]), str(realtors[3]), str(realtors[4])))
        
        conn.commit()

        
    #print(str(response['data']['report'][len(response['data']['report'])-1]))
    
    return "Complete"
