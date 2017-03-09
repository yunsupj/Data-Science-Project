#!/usr/bin/env python
import boto3
import schedule
import time
import sys
from yahoo_finance import Share
from pprint import pprint
from datetime import datetime, timedelta

#connet into firehose with boto3
firehose_client = boto3.client('firehose', region_name='us-east-1')
date = datetime.now()                                                       #today date
print("Ex) US Dallar Index: DX-Y.NYB | Apple: aapl | Google: googl")        #print example for symbols in market
# symbol1 = raw_input("#1 Stock/Curreny: ")                                 #raw_input symbol1
# symbol2 = raw_input("#2 Stock/Curreny: ")                                 #raw_input symbol2
symbol1 = sys.argv[1]                                                       #first argment (symbol1)
symbol2 = sys.argv[2]                                                       #second argment (symbol2)
symbol1 = Share(symbol1)                                                    #symbol1 with yahoo api
symbol2 = Share(symbol2)                                                    #symbol2 with yahoo api
#days_before = int(raw_input("Previous Data(Days from today): "))           #type date before today for historical data; 0 is current data
days_before = int(sys.argv[3])

def yahoo_his_years(symbols, date, days_before):
    '''
    INPUT: historical price for symbols in seleted period of time (raw_input or sys.argv) .
    OUTPUT: symbols price in str format inserted in S3 using Kinesis.
    '''
    counter = 0
    date = date - timedelta(days=days_before)
    for day in range(days_before): 
        if date.strftime('%Y-%m-%d') <= datetime.now().strftime('%Y-%m-%d'):
            try:
                sym = symbols.get_historical(date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
                response = firehose_client.put_record(DeliveryStreamName='yahoo_data', Record={'Data': str(sym)+'\n'})
                print(sym)
                date += timedelta(days=1)
                counter += 1
                print("Inserted {} days {} data.".format(counter, symbols.get_name()))
        
            except Exception:
                print("It is Holiday or Weekend.")
                date += timedelta(days=1)

def yahoo_current(symbol1, symbol2):
    '''
    INPUT: current price for symbols in previous date (put 0 day for raw_input or sys.argv).
    OUTPUT: current symbols price in str format inserted in S3 using Kinesis.
    '''
    date = datetime.now() - timedelta(days=1)
    if date.strftime('%Y-%m-%d') <= datetime.now().strftime('%Y-%m-%d'):
        try:
            sym1 = symbol1.get_historical(date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
            response = firehose_client.put_record(DeliveryStreamName='yahoo_data', Record={'Data': str(sym1)+'\n'})
            sym2 = symbol2.get_historical(date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
            response = firehose_client.put_record(DeliveryStreamName='yahoo_data', Record={'Data': str(sym2)+'\n'})
            print("Inserted {} {} data.".format(date.strftime('%Y-%m-%d'), symbol1.get_name()))
            print("Inserted {} {} data.".format(date.strftime('%Y-%m-%d'), symbol2.get_name()))
        except Exception:
            print("It is Holiday or Weekend.")

             
if __name__ == '__main__':
    if days_before == 0:
        #schedule to update data every day at 5:30 PST
        schedule.every(1).day.at("05:30").do(yahoo_current, symbol1, symbol2)
        yahoo_current(symbol1, symbol2)
        #schedule.every(1).minutes.do(yahoo_current, symbol1, symbol2)
        while True:
            schedule.run_pending()
    else:
        yahoo_his_years(symbol1, date, days_before)
        yahoo_his_years(symbol2, date, days_before)

'''
S3 url : https://console.aws.amazon.com/s3/home?region=us-east-1#&bucket=yahoo-data-final-project&prefix=2017/03/02/
S3 url Parquet : https://console.aws.amazon.com/s3/home?region=us-east-1#&bucket=yahoo-data-final-project&prefix=symbol1/
                 https://console.aws.amazon.com/s3/home?region=us-east-1#&bucket=yahoo-data-final-project&prefix=symbol2/
                 https://console.aws.amazon.com/s3/home?region=us-east-1#&bucket=yahoo-data-final-project&prefix=yahoo-df/



In order to get 10 years historical data:
python Local_yahoo_S3.py aapl msft 3650

In order to get current data, it will be updated everyday (run in background):
nohup python Local_yahoo_S3.py aapl msft 0 &
'''
