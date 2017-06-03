import getData_yahoo
import TimeSeries_Analysis_YAHOO_API_LSTM
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import glob

def pred_plot(pred_data, real_data):
    '''
    Input: predicted data & real data
    Output: compare b/t predicted data and real data
    '''
    plt.figure(figsize=(15,8))
    plt.plot(pred_data, label='Prediction', color='g', linewidth=3);
    plt.plot(real_data, label='Real Data', color='r', linewidth=3);
    plt.title('Validate Data b/w Prediction & Real', fontsize=18)
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Normalized Price (Adj Close)', fontsize=15)
    plt.legend()
    plt.show()

def future_prediction(data, days):
    '''
    Input:  test data and days which you want to predict price in future.
             ex) future_prediction(X_test, 50) --> X_test(IBM) 50 days future price prediction from today.
    Output: normalized values of future price prediction for some days from today.
            Type - numpy.ndarray
    '''
    data = data[-1]                                                                                #the most recent data use for future prediction
    ft_y_vals = []                                                                                 #the value of future price prediction
    for day in range(days):                            
        ft_win_data = data.reshape(1, days, 1)                                                       #reshape data for model input
        ft_y_val = TimeSeries_Analysis_YAHOO_API_LSTM.pred_value(model, ft_win_data).tolist()      #prediction values with pred_values function(list)
        ft_y_vals.append(ft_y_val)                                                                 #make list of value of future prices
        data = data[-(days-1):].reshape(data[-(days-1):].shape[0],)                                            #segment 50days with adding predicted price for next prediction
        data = np.append(data, ft_y_val)                        
        data = np.asarray([((e+1)/(data[0]+1))-1 for e in data])                                   #re-normalize new segmented values(first values is zero)
    ft_y_vals = np.asarray(ft_y_vals)                                                              #make numpy array type from list
    ft_y_vals = ft_y_vals.reshape((ft_y_vals.size,))                                               #change shape (50,1) to (50,)  
    return ft_y_vals    

#Main Run
if __name__=='__main__':
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'IBM']
    for sym in symbols:
        getData_yahoo.get_yahoo_csv(sym, 10)

    epochs  = 10             #set epochs, 10
    window = 50              #set window(segment or sequence), 50 days
    
    #Build model
    model = TimeSeries_Analysis_YAHOO_API_LSTM.build_model()
    
    #set the path where glob the .csv files
    path = '*.csv'
    files = glob.glob(path)
    
    #train model number of times which is the same number with symbols(for Demo 3 times)
    for f in files:  
        #split train and test data for apple and make plot for price moving and segmentation.
        X_train, y_train, X_test, y_test = TimeSeries_Analysis_YAHOO_API_LSTM.load_data(f, window)

        #Training model with list of companise stocks(symbols); 'AAPL', 'GOOGL', 'MSFT'
        print('Training...')

        #fit into model for train datas
        model.fit(X_train, y_train,                          
                  batch_size=128,
                  validation_data=(X_test, y_test),
                  epochs=epochs)

        #save model
        model.save("TimeSeries_Ananlysis_YAHOO_API_{}.h5".format(f), overwrite=True)
        print("Save Model for {}".format(f))
        
        #check time for prediction
        %%time

        #prediction with model for X_test data
        pred = TimeSeries_Analysis_YAHOO_API_LSTM.pred_value(model, X_test)

        #make plot prediction values and real values to compare
        pred_plot(pred, y_test)
        future_price = future_prediction(X_test, window)

        #append numpy array type matrixs pred and future price
        new_y_pred = np.append(pred, future_price)
    
        #make plot for IBM stock price next 50 days from 5/5/2017.
        pred_plot(new_y_pred, y_test)