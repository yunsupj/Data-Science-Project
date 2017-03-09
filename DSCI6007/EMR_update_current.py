from pyspark.sql.functions import *
from pyspark import SparkContext, SQLContext
from time import time

'''
run EMR_updata_current.py in EMR with cronjob
every day at 6AM, it will over write(store) into S3 as parquet(yahoo-symbol-price/yahoo-price-parquet).
'''
def update_current():
    '''
    INPUT: S3 stored data.
    OUTPUT: updated current price for each symbols, then over write into S3 as parquet.
    '''
    raw_yahoo_finance = spark.read.json("s3a://yahoo-data-final-project/2017/03/*/*")
    yahoo_price_df = raw_yahoo_finance.selectExpr("Adj_Close AS price", 
                                                  "Date AS date",
                                                  "Symbol")
    #yahoo_price_df.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/yahoo-price-parquet")
    #apple stock
    #symbol = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'aapl')
    #symbol.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/apple")
    
    
    apple = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'aapl')
    apple.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/apple")
    
    msft = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'msft')
    msft.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/msft")
    
    amzn = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'AMZN')
    amzn.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/amzn")
    
    googl = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'googl')
    googl.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/googl")
    
    jpm = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'JPM')
    jpm.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/jpm")

    bac = yahoo_price_df.selectExpr("price", "Date AS date").where(yahoo_price_df.Symbol == 'BAC')
    bac.write.mode('overwrite').parquet("s3a://yahoo-symbol-price/bac")

if __name__ == '__main__':
    update_current()