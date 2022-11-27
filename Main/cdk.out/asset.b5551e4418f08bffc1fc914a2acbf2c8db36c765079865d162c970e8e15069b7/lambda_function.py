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
    top = str(10)
    query='ListPrice,PostalCode,OriginatingSystemName,ListAgentEmail,ListAgentFullName,ListAgentPreferredPhone,StandardStatus,ListingId'

    url = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

    url2 = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27REColorado%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=' + query

    url_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Active%27&$select=' + query

    url2_pikes = 'https://listings.constellation1apis.com/OData/Property?$top=' + top + '&$ignorenulls=true&$filter=ModificationTimestamp%20ge%20' + z + '%20and%20OriginatingSystemName%20eq%20%27PikesPeak%27%20and%20StandardStatus%20eq%20%27Closed%27&$select=' + query

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
    for i in range(int(top)):
        agent_name_pikes = result_pikes[i]['ListAgentFullName']
        agent_name_coldo = result[i]['ListAgentFullName']

        try:
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

    n2 = response2['value']
    postal_codes = {}

    for j in range(len(n2)):

        postal_p = result_pikes[j]['PostalCode']
        postal_r = result[j]['PostalCode']

        try:
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

    # result['ListAgentEmail']
    # result['ListAgentFullName']
    # result['ListPrice']
    # result['OriginatingSystemName']
    # result['PostalCode']

    postal = heapq.nlargest(5, postal_codes, key=postal_codes.get)
    realtors = heapq.nlargest(5, dictionary, key=dictionary.get)
    average = sum(prices) / len(prices)
    median = statistics.median(prices)
    print("Average Sales Price for the Past Year: ", average)
    print("Median Sales Price for the Past Year: ", median)
    print("Top 5 Realtors for the Past Year (Based on the number of Active listed properties): ", realtors)
    print("Total Units Sold for the Past Year: ", total_units_sold)
    print("Top 5 Postal Addresses for the Past Year for Sold Properties: ", postal)
    time_period=oneYearAgoToday+'-'+today
    # average, median, realtors, total_units_sold, postal, today

    #Logic Code Ends Here

    with conn.cursor() as cur:
        #cur.execute("create table results (date_inserted varchar(255) NOT NULL, time_period varchar(255), average_price varchar(255), median_price varchar(255), total_units_sold varchar(255), postal_code_1 varchar(255), postal_code_2 varchar(255), postal_code_3 varchar(255), postal_code_4 varchar(255), postal_code_5 varchar(255), realtor_1 varchar(255), realtor_2 varchar(255), realtor_3 varchar(255), realtor_4 varchar(255), realtor_5 varchar(255), PRIMARY KEY (date_inserted))")
        
        
        ins= 'insert into results (date_inserted, time_period, average_price, median_price, total_units_sold, postal_code_1, postal_code_2, postal_code_3, postal_code_4, postal_code_5, realtor_1, realtor_2, realtor_3, realtor_4, realtor_5) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        # average, median, realtors, total_units_sold, postal, today
        
        cur.execute(ins, (str(today), str(average), str(time_period), str(median), str(total_units_sold), str(postal[0]), str(postal[1]), str(postal[2]), str(postal[3]), str(postal[4]), str(realtors[0]), str(realtors[1]), str(realtors[2]), str(realtors[3]), str(realtors[4])))
        
        conn.commit()

        
    #print(str(response['data']['report'][len(response['data']['report'])-1]))
    
    return "Complete"
