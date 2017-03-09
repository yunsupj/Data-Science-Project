from time import time
import pandas as pd
import matplotlib.pyplot as plt
from boto.s3.connection import S3Connection
from mpld3 import fig_to_html, plugins

def draw_graph():
	'''
    INPUT: load parquet from S3.
    OUTPUT: make one dataframe, then draw correlation graph.
    '''

	#load parquet files for each symbol
	aapl_df = spark.read.load("s3a://yahoo-symbol-price/apple")
	msft_df = spark.read.load("s3a://yahoo-symbol-price/msft")
	amzn_df = spark.read.load("s3a://yahoo-symbol-price/amzn")
	googl_df = spark.read.load("s3a://yahoo-symbol-price/googl")
	#jpm_df = spark.read.load("s3a://yahoo-symbol-price/jpm")
	#bac_df = spark.read.load("s3a://yahoo-symbol-price/bac")

	aapl_pd = aapl_df.toPandas().drop_duplicates('date')
	msft_pd = msft_df.toPandas().drop_duplicates('date')
	amzn_pd = amzn_df.toPandas().drop_duplicates('date')
	googl_pd = googl_df.toPandas().drop_duplicates('date')

	#date as index for every symbol
	aapl_pd.index = aapl_pd['date']
	aapl_pd = aapl_pd.drop('date', axis=1)
	aapl_pd.columns = ['aapl']

	msft_pd.index = msft_pd['date']
	msft_pd = msft_pd.drop('date', axis=1)
	msft_pd.columns = ['msft']

	amzn_pd.index = amzn_pd['date']
	amzn_pd = amzn_pd.drop('date', axis=1)
	amzn_pd.columns = ['amzn']

	googl_pd.index = googl_pd['date']
	googl_pd = googl_pd.drop('date', axis=1)
	googl_pd.columns = ['googl']

	price_df = pd.concat([aapl_pd, msft_pd, amzn_pd, googl_pd], join='outer', axis = 1).dropna(axis=0).reset_index()
	price_df['date'] = price_df['index'].convert_objects(convert_dates='coerce')
	price_df = price_df.drop('index', axis=1)
	price_df = price_df.sort_index(by='date').set_index('date')

	corr_ap_ms = pd.rolling_corr(price_df.aapl, price_df.msft, 30, min_periods=30).dropna(axis=0)
	corr_az_gl = pd.rolling_corr(price_df.amzn, price_df.googl, 30, min_periods=30).dropna(axis=0)

	fig1 = plt.figure(figsize=(12, 8))
	plt.title("Correlation AAPL & MSFT", fontsize=16)
	plt.xlabel("Date", fontsize=13)
	plt.ylabel("Correlation", fontsize=13)
	corr_ap_ms.plot();

	fig2 = plt.figure(figsize=(12, 8))
	plt.title("Correlation AMZN & GOOGL", fontsize=16)
	plt.xlabel("Date", fontsize=13)
	plt.ylabel("Correlation", fontsize=13)
	corr_az_gl.plot();

	#AWS
	conn = boto.connect_s3(host='s3.amazonaws.com')
	website_bucket = conn.get_bucket('yahoo-symbol-price')

	corr1 = "AAPL_MSFT.png"
	corr1 = "<!DOCTYPE html>\
	            <html>\
    	          <body>\
        	        <h2>Correlation</h2>\
            	      <img src=http://ec2-54-234-234-93.compute-1.amazonaws.com:8888/files/{} style='width:500px;height:350px;'>\
            	  </body>\
            	</html>".format(corr1)
	output_file = website_bucket.new_key('corr1.html')
	output_file.content_type = 'text/html'
	output_file.set_contents_from_string(corr1, policy='public-read')

	corr2 = "AMZN_GOOGL.png"
	corr2 = "<!DOCTYPE html>\
    	        <html>\
        	      <body>\
            	    <h2>Correlation</h2>\
                	  <img src=http://ec2-54-234-234-93.compute-1.amazonaws.com:8888/files/{} style='width:500px;height:350px;'>\
	              </body>\
    	        </html>".format(corr2)
	output_file = website_bucket.new_key('corr2.html')
	output_file.content_type = 'text/html'
	output_file.set_contents_from_string(corr2, policy='public-read')

if __name__ == '__main__':
	draw_graph()