import matplotlib.pylab as plt
import seaborn as sns
import numpy as np
import pandas as pd
import IPython
from IPython.display import display, HTML
import tensorflow as tf
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers import Merge
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, CSVLogger, EarlyStopping
from keras.optimizers import RMSprop, Adam, SGD, Nadam
from keras.layers.advanced_activations import *
from keras.layers import Convolution1D, MaxPooling1D, AtrousConvolution1D
from keras.layers.recurrent import LSTM, GRU
from keras import regularizers
from keras.callbacks import Callback

def load_data(symbols, window, shuffle=True, norm_window=True):
    '''
    INPUT: load data from .csv file, and split by seq(window) time seris data in seleted window of time(days).
    OUTPUT: seperate train(90%) and test data(10%) for X and y.
    '''
    sym = pd.read_csv(symbols)                        #load .csv
    data = sym.ix[:, 'adj_close'].tolist()            #make list only for adj close price
   
    # plt.figure(figsize=(15,8))
    # plt.title(symbols, fontsize=18)                   #plot stock price by date
    # plt.xlabel('Date', fontsize=15)
    # plt.ylabel('Price (Adj Close)', fontsize=15)
    # plt.plot(data)
    # plt.show()
    
    win_size = window + 1                             #set window(seq) size
    win_data = []                                     #make empty list for window data
    for i in range(len(data)-win_size):
        win_data.append(data[i:i+win_size])
    
    if norm_window:                                   #normalize window data
        win_data = norm_windows(win_data)
    else:
        win_data = np.asarray(win_data)

    r = round(0.9 * win_data.shape[0])                #ready to seperate train and test data
    tr = win_data[:int(r), :]                         #seperate for train, 90%
    te = win_data[int(r):, :]                         #seperate for test, 10%
    
    if shuffle:                                       #shuffling for train and label
        np.random.shuffle(tr)                         #shuffle when make model, but no shuffle for prediction
    
    # plt.figure(figsize=(15,8))
    # plt.xlabel('Date', fontsize=15)
    # plt.ylabel('Normalized Price (Adj Close)', fontsize=15)
    # plt.plot(tr)
    # plt.show()
    
    X_train = tr[:, :-1]                              #seperate x and y for train data
    y_train = tr[:, -1]
    X_test = te[:, :-1]                               #seperate x and y for test data
    y_test = te[:, -1]     
    X_train = np.expand_dims(X_train, axis=2)         #expand dimension for train   
    X_test = np.expand_dims(X_test, axis=2)           #expand dimension for test
    return [X_train, y_train, X_test, y_test]

def norm_windows(win_data):
    '''
    INPUT: list of window data.
    OUTPUT: normalize window data(list), and put into matrix.
    '''
    norm_data = []                                    #make empty list for normalized window data
    for win in win_data:
        norm_window = [ele/win[0]-1 for ele in win]   #normalize [first element is zero for each window(seq) data]
        norm_data.append(norm_window)
    return np.asarray(norm_data)

def build_model(input_dim=1, output_dim=50, hidden_units=128, final_output_dim=1):
    """
    Input: Input and output dimension.
    Output: Build the LSTM model based on input, output dimension, and compailing with adam optimazer with mse.
    """
    print('Build model...')
    
    model = Sequential()                           #set the model       

    model.add(LSTM(input_dim=input_dim,            #add LSTM dense 
                   output_dim=output_dim, 
                   return_sequences=True))
    model.add(Dropout(0.2))                        #apply 20% dropout to avoid overfitteing

    model.add(LSTM(hidden_units, 
                   return_sequences=False))        #add LSTM dense
    model.add(Dropout(0.2))

    model.add(Dense(output_dim=final_output_dim))  #apply 20% dropout to avoid overfitteing
    model.add(Activation('linear'))                #apply linear as an activation

    model.compile(loss='mse',                      #compile with adam and mse
                  optimizer='adam')

    model.summary()
    return model

def pred_value(model, data):
    '''
    Input: model and data.
    Output: predict each timestep of data, it is predicted 1 step ahead each timestep.
    '''
    pred = model.predict(data)                 #predict values from data
    pred = np.reshape(pred, (pred.size,))      #reshape to reduce dimesion into the same shape as y values
    return pred

def future_prediction(data, days):
    '''
    Input:  test data and days which you want to predict price in future.
             ex) future_prediction(X_test, 50) --> X_test(IBM) 50 days future price prediction from today.
    Output: normalized values of future price prediction for some days from today.
            Type - numpy.ndarray
    '''
    data = data[-1]                                             #the most recent data use for future prediction
    ft_y_vals = []                                              #the value of future price prediction
    for day in range(days):                            
        ft_win_data = data.reshape(1, 50, 1)                    #reshape data for model input
        ft_y_val = pred_value(model, ft_win_data).tolist()      #prediction values with pred_values function(list)
        ft_y_vals.append(ft_y_val)                              #make list of value of future prices
        data = data[-49:].reshape(data[-49:].shape[0],)         #segment 50days with adding predicted price for next prediction
        data = np.append(data, ft_y_val)                        
        data = np.asarray([((e+1)/(data[0]+1))-1 for e in data]) #re-normalize new segmented values(first values is zero)
    ft_y_vals = np.asarray(ft_y_vals)                            #make numpy array type from list
    ft_y_vals = ft_y_vals.reshape((ft_y_vals.size,))             #change shape (50,1) to (50,)  
    return ft_y_vals

    
