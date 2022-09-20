"""
Ingestion pipeline to fetch Mutual Fund data from AMFI website

Usage: ./mfscript.py

Author: Mainak Gachhui
"""
import time
import requests
import psycopg2
import csv
from config import *

def fetch_endpoint_data(endpoint):
    response = requests.get(endpoint).text
    # Split response into lines
    # Ignore: blank lines, non-nav data like scheme type and mutual fund
    response_lines = [line for line in response.splitlines() if line.strip() != "" and ";" in line ]
    return response_lines

def fetch_latest_nav_data():
    return fetch_endpoint_data(endpoint_latest)

def fetch_historical_nav_data(from_date, to_date):
    return fetch_endpoint_data(endpoint_history.format(from_date, to_date))

def write_response_to_temp_csv(response_lines):
    # Fix csv header to match db columns
    for k,v in headerdict.items():
        response_lines[0] = response_lines[0].replace(k, v)
    csv_rows = [line.split(";") for line in response_lines]
    # writing to csv file 
    with open(temp_file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_rows)   

def copy_from_temp_csv(is_latest):
    conn = psycopg2.connect(**dbparams)
    conn.autocommit = False
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE {};".format(nav_temp_table))
    if is_latest:
        cursor.execute('''COPY {}(scheme_code,isin_div_payout_growth,isin_div_reinvestment,scheme_name,nav,nav_date) 
            FROM '{}' csv HEADER;'''.format(nav_temp_table, temp_file_path))
        cursor.execute('''INSERT INTO {}(scheme_code,isin_div_payout_growth,isin_div_reinvestment,scheme_name,nav,nav_date)
            SELECT scheme_code,isin_div_payout_growth,isin_div_reinvestment,scheme_name,nav::real as nav,nav_date 
            FROM {} 
            WHERE nav_date > CURRENT_DATE-3 AND nav != 'N.A.'
            ON CONFLICT DO NOTHING'''.format(nav_table, nav_temp_table))
    else:
        cursor.execute('''COPY {}(scheme_code,scheme_name,isin_div_payout_growth,isin_div_reinvestment,nav,repurchase_price,sale_price,nav_date) 
            FROM '{}' csv HEADER;'''.format(nav_temp_table, temp_file_path))
        cursor.execute('''INSERT INTO {}(scheme_name,scheme_code,isin_div_payout_growth,isin_div_reinvestment,nav,nav_date)
            SELECT scheme_name,scheme_code,isin_div_payout_growth,isin_div_reinvestment,nav::real as nav,nav_date 
            FROM {} 
            WHERE nav != 'N.A.'
            ON CONFLICT DO NOTHING'''.format(nav_table, nav_temp_table))
    conn.commit()
    cursor.close()

def incremental_load():
    start_time = time.time()
    response_data = fetch_latest_nav_data()
    write_response_to_temp_csv(response_data)
    copy_from_temp_csv(is_latest=True)
    end_time = time.time()
    print("Incremental load took {} seconds".format(str(end_time - start_time)))

def historical_load(fromdate, todate):
    start_time = time.time()
    response_data = fetch_historical_nav_data(fromdate, todate)
    write_response_to_temp_csv(response_data)
    copy_from_temp_csv(is_latest=False)
    end_time = time.time()
    print("Historical load from {} to {} took {} seconds".format(fromdate, todate, str(end_time - start_time)))

historical_load("1-Jan-2020", "31-Dec-2020")
historical_load("1-Jan-2021", "31-Dec-2021")
historical_load("1-Jan-2022", time.strftime('%Y-%m-%d'))
incremental_load()
