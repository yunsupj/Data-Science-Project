import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def cal_exp(symbol, num_of_years, days_per_year=261):
    #calculate the compound annual growth rate(CAGR), it will use as mean return input(mu) 
    days = len(symbol.index)
    CAGR = ((((symbol['adj_close'][-1]) / symbol['adj_close'][0])) ** (1 / (num_of_years))) - 1
    print('Compound Annual Growth Rate(CAGR): {}%'.format(np.round(CAGR*100, 2)))
 
    #create a series of percentage return and calculate the annual volatility
    symbol['per_return'] = symbol['adj_close'].pct_change()
    volatility = symbol['per_return'].std()
    #volatility = symbol['ndaily_change'].std()
    annual_volat = volatility * np.sqrt(days_per_year)
    #print('Annual Volatility: {}%'.format(np.round(annual_volat*100, 2)))
    
    return CAGR, annual_volat

def cal_log_exp(symbol, num_of_years, days_per_year=261):
    #calculate the compound annual growth rate(CAGR), it will use as mean return input(mu) 
    days = len(symbol.index)
    CAGR = ((((symbol['log_adj_close'][-1]) / symbol['log_adj_close'][0])) ** (1 / (num_of_years))) - 1
    print('Compound Annual Growth Rate(CAGR): {}%'.format(np.round(CAGR*100, 2)))
 
    #create a series of percentage return and calculate the annual volatility
    symbol['log_per_return'] = symbol['log_adj_close'].pct_change()
    volatility = symbol['log_per_return'].std()
    #volatility = symbol['nlog_daily_change'].std()
    annual_volat = volatility * np.sqrt(days_per_year)
    #print('Annual Volatility: {}%'.format(np.round(annual_volat*100, 2)))
    
    return CAGR, annual_volat

def MC_simulator(symbol, days, mu, vl, n_simulation):
    #Define Variables
    start_pri = symbol['adj_close'][-1]        #starting gold price
    days = days_per_year                       #number of trading days
    mu = CAGR                                  #annual return (compound annual growth)
    vl = annual_volat                          #volatility
    simulations = []                           #make empty list for draw histgram whole simulation
    
    #make for loop for multiple times of simulation
    for _ in range(n_simulation):
        #make list of daily returns by random normal distribution
        day_return = np.random.normal(mu/days, vl/np.sqrt(days), days)+1

        #set start price and make list of price by random day return
        list_pri = [start_pri]
        for i in day_return:
            list_pri.append(list_pri[-1]*i)
    
        #plotting for list_pri prediction next 1 year (261 days).
        plt.plot(list_pri)
        
        #append last gold price of each simulation
        simulations.append(list_pri[-1])
        
    plt.title('GOLD Price Random Walk (Monte Carlo) Simulation', fontsize=20)
    plt.ylabel('Adj. Price', fontsize=15)
    plt.xlabel('Days', fontsize=15)
    plt.axhline(np.mean(simulations), color='r', linestyle='dashed', linewidth=3)
    plt.axhline(np.mean(simulations)+2*np.std(simulations), color='g', linestyle='dashed', linewidth=3)
    plt.axhline(np.mean(simulations)-2*np.std(simulations), color='g', linestyle='dashed', linewidth=3)
    plt.show()
    
    #draw histogram for last gold price for mutliple simulations
    plt.hist(simulations, bins=100)
    plt.title('Distribution for GOLD Price in Last Day from Random Walk Simulation', fontsize=20)
    plt.ylabel('Frequency', fontsize=15)
    plt.xlabel('Adj. Price', fontsize=15)
    plt.axvline(np.percentile(simulations, 5), color='r', linestyle='dashed', linewidth=2)
    plt.axvline(np.percentile(simulations, 95), color='r', linestyle='dashed', linewidth=2)
    plt.show()
    print('== Evaluation =====================================')
    print('* Mean Price: ${}'.format(np.round(np.mean(simulations), 2)))
    print('* Std. : ${}'.format(np.round(np.std(simulations))))
    print('* Std. Lower & Upper Adj. Price: [${0}, ${1}]'.format(np.round(np.mean(simulations)-2*np.std(simulations)),
                                                                 np.round(np.mean(simulations)+2*np.std(simulations))))
    print('---------------------------------------------------')
    print('*  5% Quantile Price: ${}'.format(np.round(np.percentile(simulations, 5))))
    print('* 95% Quantile Price: ${}'.format(np.round(np.percentile(simulations, 95))))
    print('---------------------------------------------------')
    print('* 25% Quantile Price: ${}'.format(np.round(np.percentile(simulations, 25))))
    print('* 75% Quantile Price: ${}'.format(np.round(np.percentile(simulations, 75))))
    print('===================================================')
    return simulations

def com_plot():
    #plot gold price 2017
    plt.figure(figsize=(15, 8))
    plt.plot(gold_2017['adj_close'])
    plt.title('2017 Gold Price ($)', fontsize=20)
    plt.ylabel('Adj. Price', fontsize=15)
    plt.xlabel('Date', fontsize=15)
    plt.axhline(np.mean(gold_2017['adj_close']), color='r', linestyle='-', linewidth=2, label='2017 Mean')
    plt.axhline(np.mean(gold_2017['adj_close'])+2*np.std(gold_2017['adj_close']), color='g', linestyle='-', linewidth=2, label='2017 2xSigma')
    plt.axhline(np.mean(gold_2017['adj_close'])-2*np.std(gold_2017['adj_close']), color='g', linestyle='-', linewidth=2, label='2017 2xSigma')
    plt.axhline(np.mean(mc_sim), color='r', linestyle=':', linewidth=2, label='Sim. Mean')
    plt.axhline(np.mean(mc_sim)+2*np.std(mc_sim), color='g', linestyle=':', linewidth=2, label='Sim. 2xSigma')
    plt.axhline(np.mean(mc_sim)-2*np.std(mc_sim), color='g', linestyle=':', linewidth=2, label='Sim. 2xSigma')
    plt.legend()
    plt.show()

    print('== Evaluation Original Price =======================')
    print('* Mean Price: ${}'.format(np.round(np.mean(gold_2017['adj_close']), 2)))
    print('* Std. : ${}'.format(np.round(np.std(gold_2017['adj_close']))))
    print('* Std. Lower & Upper Adj. Price: [${0}, ${1}]'.format(np.round(np.mean(gold_2017['adj_close'])-2*np.std(gold_2017['adj_close'])),
                                                                 np.round(np.mean(gold_2017['adj_close'])+2*np.std(gold_2017['adj_close']))))
    print('===================================================\n')
    print('== Evaluation Simulation Price =====================')
    print('* Mean Price: ${}'.format(np.round(np.mean(mc_sim), 2)))
    print('* Std. : ${}'.format(np.round(np.std(mc_sim))))
    print('* Std. Lower & Upper Adj. Price: [${0}, ${1}]'.format(np.round(np.mean(mc_sim)-2*np.std(mc_sim)),
                                                                 np.round(np.mean(mc_sim)+2*np.std(mc_sim))))
    print('===================================================')     

#Main Run
if __name__=='__main__':
    #load the gold adj. price data(1979 ~ 2016) and make index for date as datetime type
    gold = pd.read_csv('gold.csv')
    gold['Date'] = pd.DatetimeIndex(gold['Date'])
    gold = gold.set_index('Date')
    
    #apply log transform to the original gold price
    gold['log_adj_close'] = gold['adj_close'].apply(lambda x: np.log(x))

    #load the gold data(2017) in order to compare with random walk result
    gold_2017 = pd.read_csv('gold_2017.csv')
    gold_2017['Date'] = pd.DatetimeIndex(gold_2017['Date'])
    gold_2017 = gold_2017.set_index('Date')

    #cut the data set as ngold - 2006 ~ 2016 
    last_11_years = -(261*11) + 1
    ngold = gold[last_11_years:]
    
    #calculate mean of days in years in order to apply frequency for seasonality
    uniq_years = sorted(list(set(ngold.index.year)))           #uniq. years (2004 ~ 2016)
    year_count = []                                            #make empty list for counting days each year

    for i in uniq_years:
        year_count.append(len(ngold[ngold.index.year == i]))
    days_per_year = int(np.round(np.mean(year_count), 0))      #calculate the mean days in years                     #calculate the mean days in years

    #number of years for CAGR calculation 
    days = len(ngold.index)
    num_of_years = days/days_per_year

    #calculate GOLD Price
    CAGR, annual_volat = cal_exp(ngold, num_of_years, days_per_year)

    #calculate logged GOLD Price 
    log_CAGR, log_annual_volat = cal_log_exp(ngold, num_of_years, days_per_year)

    #Random walk simulation 10000 tims
    mc_sim = MC_simulator(ngold, days_per_year, CAGR, log_annual_volat, 500)
    com_plot()
