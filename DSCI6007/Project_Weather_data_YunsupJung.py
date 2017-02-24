'''
Author: Yunsup Jung
DSCI6007 Project: Analysis weather data in order to use investing present, 
														cordinating clother information,
														other business predition.
'''

import pyowm

API_key = '16f3c0560f0938280ba5681ca0e82feb'
owm = pyowm.OWM(API_key)                                    #provide a valid API key

forecast = owm.daily_forecast('sanfrancisco,us')            #forecast weather in San Francisco, US 
tomorrow = pyowm.timeutils.tomorrow()
forecast.will_be_sunny_at(tomorrow)  

observation = owm.weather_at_place('sanfrancisco,us')       #current weather in San Francisco, US 
w = observation.get_weather()
print(w)     

#Output : <pyowm.webapi25.weather.Weather - reference time=2017-02-12 17:18:22+00, status=Clear>                 
