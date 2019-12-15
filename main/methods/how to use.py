import yfinance as yf
import numpy as np

# import pandas_datareader.data as pdr


# how data is fetched in functions
yfdata = yf.download('AAPL',start='2018-05-30', end='2019-07-30', interval='60m')

# =============================================================================
# start=date(2017,1,1)
# end=date.today()
# ticker='AAPL'
# database='' 
# #there is no updating free daily stock price database on quandl, Premium database is the choice when you use it
# qkey='msyfBiEAuisn2CaoQWYk'
# quandldata=pdr.DataReader(database+'/'+ticker,'quandl',start,end,access_key=qkey)      
# =============================================================================

'''
pick interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
default interval='1d'
'1h' not suggested, use '60m', which has accurate time index
each time index is the start time of corresponding period
start and end dates should have format '%Y-%m-%d'
data on start and end dates is not included
'''

import functions
stock = functions.Generic('goog', '2011-09-01', '2012-09-09', interval='1d')
stock.stock_chart(chart_type='candlestick', has_volume=True) # candlestick chart
stock.stock_chart(chart_type='line', has_volume=True) # line chart

data = stock._data # look inside data

stock.statistic1_MMD() # maximum drawdown value
stock.statistic1_MMD(get_figure=True) # maximum drawdown figure

ema = stock.indicator1_EMA(N=12) # exponential moving average series
stock.indicator1_EMA(N=12, get_figure=True) # exponential moving average figure

so = stock.indicator2_SO(N=14) # Stochastic Oscillator
stock.indicator2_SO(N=14, get_figure=True)

is_extreme, trend_scale = stock.indicator3_Top_Bottom(K=5, recognition_method='height') # top and bottom positions
is_extreme, trend_scale = stock.indicator3_Top_Bottom(K=6, show_price_change=True, recognition_method='height') 
stock.indicator3_Top_Bottom(K=13, get_figure=True)
stock.indicator3_Top_Bottom(K=5, get_figure=True, recognition_method='height')

satisfactory_K = stock.best_K(left=2, right=11, recognition_method='height') 
satisfactory_K = stock.best_K(left=4, right=50, recognition_method='width') 

high_volume = stock.indicator4_high_volume(K=7, recognition_method='width') 
stock.indicator4_high_volume(K=10, get_figure=True, recognition_method='width')
# when you want to get extreme point of fluctuating variable, 'width' is good for recognition_method

pattern_info = stock.candlestick_pattern_detector()

array = np.ones(len(stock.close))
future_trend = stock.future_trend(array=array, K=5) # only for recognition_method='height'

stock.indicator5_MACD(get_figure=True)
stock.indicator5_MACD(fast_period=12, slow_period=26, signal_period=9, get_figure=True)

pbv = stock.price_by_volume()
stock.price_by_volume(get_figure=True)



import strategies
weight = [0.5, 0.3, 0.2]
strategy = stock.Strategy1_MACD_based(fast_period=12, slow_period=26, signal_period=9, K=4, weight=weight)
strategy = stock.Strategy2_AIP(K=30)

stock.backtest(*strategy, get_figure='signal')
stock.backtest(*strategy, get_figure='return')
summary = stock.backtest(*strategy)







import analysis
from functools import partial
DOWJONES = ['MMM', 'AXP', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'DWDP',
            'XOM', 'WBA' ,'GS', 'HD', 'INTC', 'IBM', 'JNJ', 'JPM', 'MCD',
            'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH', 'UTX', 'VZ',
            'V', 'WMT', 'DIS'] # len(DOWJONES) = 30
A = analysis.Aggregate(DOWJONES, '2019-01-08', '2019-11-30', interval='1d')
strategy_func = partial(strategies.Strategy1_MACD_based, fast_period=12, slow_period=26, signal_period=9, K=4)
weight = [0.5, 0.3, 0.2]
A.strategy_evaluate1(strategy_func, weight)
best_weight, best_return = A.strategy_optimization(strategy_func)









