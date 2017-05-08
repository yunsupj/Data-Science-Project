from yahoo_finance import Share
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def get_yahoo_csv(symbols, years_before):
    '''
    INPUT: historical price for symbols in seleted period of time.
    OUTPUT: save as .csv file in each symbols.
    '''
    days_before = years_before * 365                          #trasfer years into days
    today = datetime.now().strftime('%Y-%m-%d')               #make today as str
    date = datetime.now() - timedelta(days=days_before)       #date is days before from today

    symbol = Share(symbols)                                 
    sym = pd.DataFrame(symbol.get_historical(date.strftime('%Y-%m-%d'), today))[::-1]
    sym.columns = map(str.lower, sym.columns)
    sym.index = sym['date']
    sym = sym.drop(['symbol', 'date'], axis=1)
    
    print("Inserted {} days {} data.".format(days_before, symbol.get_name()))
    sym.to_csv("{}.csv".format(symbol.get_name()))
    return sym