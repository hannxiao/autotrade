import numpy as np
import pandas as pd
from collections import deque 
from bisect import bisect_left



def extreme_point(array, K, recognition_method, only_max=False):
    # recognition_method == 'width': (Sliding Window Maximum)
    # get local extreme point of array within redius K, K is integer    
    # recognition_method == 'height': ignore all trends with change less than K percent, K is float
    # or we can say, if one period has change more than K%, then regard it as a trend
    is_extreme = np.zeros(len(array))
    N = len(array)
    if recognition_method == 'width':
        if only_max == False:        
            S = deque() 
        G = deque() 
        
        for i in range(K):
            if only_max == False:               
                while (len(S) > 0 and array[S[-1]] >= array[i]): 
                   S.pop() 
                S.append(i) 
                   
            while (len(G) > 0 and array[G[-1]] <= array[i]): 
                G.pop()          
            G.append(i)
        # check if position 0 is extreme point            
        if G[0] == 0:
            is_extreme[0] = 1 
        elif only_max == False and S[0] == 0:
            is_extreme[0] = -1 
        
        for i in range(K, N): 
            if only_max == False:               
                while (len(S) > 0 and S[0] <= i-2*K+1): 
                    S.popleft() 
                while (len(S) > 0 and array[S[-1]] >= array[i]): 
                    S.pop()  
                S.append(i) 
                if S[0] == i-K+1:
                    is_extreme[i-K+1] = -1   
                    
            while (len(G) > 0 and G[0] <= i-2*K+1): 
                G.popleft()                
            while (len(G) > 0 and array[G[-1]] <= array[i]): 
                G.pop()
            G.append(i) 
            if G[0] == i-K+1:
                is_extreme[i-K+1] = 1 
    
        for j in range(N-K+1, N):
        # j is the index of is_extreme, j=i-K+1
            if only_max == False:               
                while S[0] <= j-K: 
                    S.popleft() 
                if S[0] == j:
                    is_extreme[j] = -1 
                
            while G[0] <= j-K: 
                G.popleft()                
            if G[0] == j:
                is_extreme[j] = 1 
    elif recognition_method == 'height':
        high_ind = 0 
        high = array[0]
        low_ind = 0
        low = array[0]
        trend_ind = 0
        for i in range(N):
            if trend_ind != 1:
                if array[i]/low-1 > K/100:
                    is_extreme[low_ind] = -1
                    trend_ind = 1
                    high = array[i]
                    high_ind = i
                if array[i] < low:
                    low_ind = i
                    low = array[i]                 
                
            if trend_ind != -1:
                if 1-array[i]/high > K/100:
                    is_extreme[high_ind] = 1
                    trend_ind = -1
                    low = array[i]
                    low_ind = i                
                if array[i] > high:
                    high_ind = i
                    high = array[i]     
        
        
        if trend_ind == 1:
            is_extreme[high_ind] = 1 
        elif trend_ind == -1:
            is_extreme[low_ind] = -1 
            
    return is_extreme 

def fill_is_extreme(array, array_extreme): # second parameter is where the func works on
# fill vector with 2 and -2, representing rising and falling trend         
    array_extreme_ind = np.nonzero(array_extreme)[0]
    last_ind = array_extreme_ind[0]
    for i in array_extreme_ind[1:]:
        array_extreme[last_ind+1:i] = [4*(array[i]>array[last_ind])-2]*(i-last_ind-1)
        last_ind = i

def EMA(array, N):
    # calculate Exponential Moving Average
    # N is typically 12 or 26
    # use MA(N) as initial value (with N-1 preceding None)
    # here we assume missing values are sparse
    ema = [None]*(N-1)
    ema.append(sum(array[0:N])/N)
    for i in range(N, len(array)):
        ema.append(round(((N-1)*ema[-1]+2*array[i])/(N+1), 2))
    return ema

def ExtremeOfPrecedingN(array, N, extremeType):
    # extreme value of N preceding numbers at each number in array
    L = len(array)
    if L <= N:
        return [None] * L
    output = [None] * N
    if extremeType == 'high':
        Qi = deque()  
        for i in range(N): 
            while Qi and array[i] >= array[Qi[-1]] : 
                Qi.pop() 
            Qi.append(i);
        for i in range(N, L):
            output.append(array[Qi[0]])
            while Qi and Qi[0] <= i-N: 
                Qi.popleft()  
            while Qi and array[i] >= array[Qi[-1]] : 
                Qi.pop() 
            Qi.append(i) 
        return output
    # the same but for lows
    elif extremeType == 'low':
        Qi = deque()  
        for i in range(N): 
            while Qi and array[i] <= array[Qi[-1]] : 
                Qi.pop() 
            Qi.append(i);
        for i in range(N, L):
            output.append(array[Qi[0]])
            while Qi and Qi[0] <= i-N: 
                Qi.popleft()  
            while Qi and array[i] <= array[Qi[-1]] : 
                Qi.pop() 
            Qi.append(i) 
        return output    
    else:
        raise Exception("Wrong input for 'extremeType', use 'high' or 'low' only.")

def future_trend(array, K, is_extreme, price): # use this function to evaluate a pattern
    # array consists of 0 and 1, determine which position to consider
    # is_extreme defines trend, K is the relevant parameter
    # the price vector is typically 'Close'
    # warning: for K when recognition_method == 'height'
    future_trend = pd.DataFrame(columns=['key_point', 'future_trend(%)', 'distance_to_extreme'])    
    extreme_point = np.nonzero(is_extreme != 0)[0] 
    is_key_point = array
    key_point = np.nonzero(is_key_point != 0)[0] 
    for i in range(len(key_point)):
        pos = bisect_left(extreme_point, key_point[i])
        # only consider price within range centered extreme price, radius K/300. You can also set it K/200
        # calculate future trend, namely how far price can go from a certain point
        if pos != len(extreme_point):
            if pos != len(extreme_point)-1 and abs(price[extreme_point[pos]]/price[key_point[i]]-1) < K/200:
                # here K/200 is a customized number representing dropping amount to stop loss
                price_change = price[extreme_point[pos+1]]/price[key_point[i]]-1
                price_change = round(100*price_change, 2)
                trend_size = price[extreme_point[pos]]-price[extreme_point[pos-1]]
                distance_to_extreme = min(abs((price[extreme_point[pos]]-price[key_point[i]])/trend_size),
                                          abs((price[extreme_point[pos-1]]-price[key_point[i]])/trend_size))
                future_trend = future_trend.append({'key_point': key_point[i],
                                                    'future_trend(%)': price_change, 
                                                    'distance_to_extreme': distance_to_extreme},
                                                     ignore_index=True)
            elif pos != 0:
                price_change = price[extreme_point[pos]]/price[key_point[i]]-1
                price_change = round(100*price_change, 2)
                trend_size = price[extreme_point[pos]]-price[extreme_point[pos-1]]
                distance_to_extreme = min(abs((price[extreme_point[pos]]-price[key_point[i]])/trend_size),
                          abs((price[extreme_point[pos-1]]-price[key_point[i]])/trend_size))
                future_trend = future_trend.append({'key_point': key_point[i],
                                                    'future_trend(%)': price_change, 
                                                    'distance_to_extreme': distance_to_extreme},
                                                     ignore_index=True)
    return future_trend  

def candlestick_pattern_detector(instance):
    pattern_info = pd.DataFrame()
    data = instance._data
    data = data.values
    openp, highp, lowp, closep, _, volume = [data[:,i] for i in range(data.shape[1])]
    
    is_hanging_man = np.zeros(len(closep))
    for i in range(len(is_hanging_man)):
        if highp[i]-max(openp[i], closep[i]) < abs(openp[i]-closep[i])*0.33 and lowp[i] < 3.5*min(openp[i], closep[i])-2.5*max(openp[i], closep[i]):
            is_hanging_man[i] = 1
    pattern_info['is_hanging_man'] =  is_hanging_man    
    # the hanging man pattern request a small upper shadow, and a long low tail, typically > 2 or 3 times body
    # hanging man is the name used in uptrend, while hammer is the same pattern when it's downtrend 
    # upper shadow : body < 1 : 3, low tail : body > 2.5 : 1 
    
    is_engulfing = np.zeros(len(closep))
    for i in range(len(is_engulfing)-1):
        if closep[i+1] > max(openp[i], closep[i]) and openp[i+1] < min(openp[i], closep[i]) and closep[i] < openp[i]*1.002:
            is_engulfing[i+1] = 1 # bullish
        elif openp[i+1] > max(openp[i], closep[i]) and closep[i+1] < min(openp[i], closep[i]) and openp[i] > closep[i]*1.002:
            is_engulfing[i+1] = -1 # bearish
    # the length of 0.2% is considered small enough to be ignorable
    pattern_info['is_engulfing'] =  is_engulfing    
    return pattern_info 

def MaximumDrawdown(array):
    # calculate Maximum Drawdown
    # It measures the largest single drop from peak to bottom
    arr = pd.Series(array)
    i = ((np.maximum.accumulate(arr)-arr)/np.maximum.accumulate(arr)).idxmax()
    j = (arr[:i]).idxmax()
    maximum_drawdown = (arr[j]-arr[i])/arr[j]
    return maximum_drawdown

def backtest(data, trade_signal):
    # initial cash is 10000, assume buying or selling with close price
    
    # 'trade_signal' deliver the information of trading:
    # the element of trade_signal is a tulple: (number, numberType, operationType)
    # sign of number indicates: negative(short position), positive(long position), none(keep position: do nothing)
    
    # number_type: 'stock', 'money', 'percentage'
    # which mean number of stocks to trade, amount of money used to trade, percentage of asset used to trade
    
    # operationType: 'set', 'vary'
    # indicates whether the number is the position itself or variance of the position
    close = data['Close']
    stock_shares, asset = [], []
    last_cash, last_stock, last_total = 10000, 0, 10000
    
    for i in range(len(trade_signal)):
        if trade_signal[i]:
            if trade_signal[i][1] == 'stock':
                stock_value = trade_signal[i][0]*close[i]
            elif trade_signal[i][1] == 'value':
                stock_value = trade_signal[i][0]                   
            elif trade_signal[i][1] == 'percentage':
                stock_value = trade_signal[i][0]*last_total
            else:
                raise Exception('strategy_type not input')
                
            if trade_signal[i][2] == 'vary':                        
                last_cash -= stock_value
                last_stock += stock_value/close[i]
            elif trade_signal[i][2] == 'set':  
                last_cash += last_stock * close[i] - stock_value
                last_stock = stock_value/close[i]
                
        last_total = last_cash + last_stock * close[i]
        stock_shares.append(last_stock)
        asset.append(last_total)                
    return stock_shares, asset 


def NextPossibleOrderType(string):
    if string in {'entry', 'size'}:
        return {'size', 'exit'}
    elif string in {'exit', None}:
        return {'entry'}
    else:
        raise Exception("Incorrect input, should be 'entry', 'size', 'exit' or None")

def StrategyGenerator(data, functions):
    close = data['Close']
    positions, equity = [], []
    orders = []
    asset = {'cash': 10000, 'position': 0, 'total': 10000}
    for i in range(len(close)):
        order = None
        for func, infoDic in functions:
            # functions: [(function1, infoDic1), (function2, infoDic2), ...]
            # 'infoDic' contains pre-calculated nummbers used in 'func'
            # namely all the needed information from 'data' except asset, orders, i
            try:
                last_order_type = orders[-1]['order_type']
            except:
                last_order_type = None
            if func.order_type in NextPossibleOrderType(last_order_type):
                temp = func(infoDic, asset, orders, i)
                if temp:
                    temp['order_type'] = func.order_type
                    temp['event_type'] = func.__name__                    
                    if not order:
                        order = temp
                    else:
                        # setting below needs improvement.
                        # only available for current-price-driven orders
                        if order['order_type'] == temp['order_type']:
                            if (order['order_price'] >= temp['order_price']) == (temp['order_price'] >= data['Open'][i]):
                                order = temp
                        elif temp['order_type'] == 'exit':
                            order = temp
# =============================================================================
#                         raise Exception('Two events in a same time unit.\norder1: {0}, {1}, {2}, {3}. \norder2: {4}, {5}, {6}, {7}. \nDate: {8}, Open: {9}, Close: {10}, High: {11}, Low: {12}'.format(order['event_type'],
#                                         order['change_type'], order['amount'], order['order_price'],
#                                         temp['event_type'], temp['change_type'], temp['amount'], temp['order_price'],
#                                         data['Date'][i], data['Open'][i], data['Close'][i], data['High'][i], data['Low'][i]))
#                         
# =============================================================================
        if order:                        
            if order['amount_type'] == 'stock':
                trading_value = order['amount']*order['order_price']
            elif order['amount_type'] == 'value':
                trading_value = order['amount']                   
            elif order['amount_type'] == 'percentage':
                trading_value = order['amount']*asset['total']
            else:
                raise Exception('strategy_type not input')
                
            if order['change_type'] == 'vary':
                position_variation = int(trading_value/order['order_price'])                    
            elif order['change_type'] == 'set':
                position_variation = int(trading_value/order['order_price']) - asset['position']

            asset['cash'] -= position_variation*order['order_price']
            asset['position'] += position_variation
            
            orders.append({'order_price': order['order_price'],
                           'event_type': order['event_type'],
                           'order_type': order['order_type'],
                           'position_variation': position_variation,
                           'i': i}) # record orders  
        
        
        asset['total'] = asset['cash'] + asset['position'] * close[i]
        positions.append(asset['position'])
        equity.append(asset['total'])
    ordersData = [[orders[k]['i'], round(orders[k]['order_price'], 2),
                   orders[k]['event_type'], orders[k]['order_type'],
                   orders[k]['position_variation']] for k in range(len(orders))]
    return positions, equity, ordersData

def GetOutput(data, functions):
    positions, equity, ordersData = StrategyGenerator(data, functions)
    output = {}    
    output['equity'] = {'name': 'return', 'data': equity, 'position': 'bottom1',
          'type': 'line'}
    #toolFuncs.MaximumDrawdown(asset)   
    output['positions'] = {'name': 'position', 'data': positions, 'position': 'bottom2', 'type': 'bar'}
    output['ordersData'] = {'name': 'orders', 'data': ordersData, 'position': 'main', 'type': 'scatter'}
    return output

def OrderTypeEntry(func):
    func.order_type = 'entry'
    return func

def OrderTypeExit(func):
    func.order_type = 'exit'
    return func

def OrderTypeSize(func):
    func.order_type = 'size'
    return func

def StrategyAnalyses(data, equity, positions, ordersData):
    # start with 10000 equity
    orders = [dict(zip(['i', 'order_price', 'event_type', 'order_type',
                        'position_variation'], orderdata)) for orderdata in ordersData]
    close = data['Close']
    L = len(close)
    cashes = [equity[j] - close[j] * positions[j] for j in range(L)]
    Yrs = L/250
    
    
    
    # rate of profit 
    profit= equity[-1]/10000 - 1    
    # average annual return 
    average_annual_return = profit/Yrs
    # benchmark returns
    benchmark_return = close[-1]/close[0] - 1    
    # annual benchmark return 
    annual_benchmark_return = benchmark_return/Yrs
    # number of trade 
    num_trades = sum([order['order_type'] == 'exit' for order in orders])
    # winning trades
    winning_trades = 0
    last_entry_equity = -1
    for order in orders:
        if order['order_type'] == 'entry':
            last_entry_equity = cashes[order['i']] + order['order_price'] * positions[order['i']]
        elif order['order_type'] == 'exit' and cashes[order['i']] + order['order_price'] * positions[order['i']] > last_entry_equity:
            winning_trades += 1
    
    # losing trades    
    losing_trades = num_trades - winning_trades


    # average annual drawdown
    
    # maximum drawdown
    
    # average profit per trade
    average_profit_per_trade = profit/num_trades
    
    # gain to pain ratio
    
    # sharpe ratio
    
    result = {}
        
    result['rate_of_profit'] = '{0}%'.format(round(100*profit, 2))
    result['time_length'] = L
    if data['Interval'] == '1d':
        result['average_annual_return'] = '{0}%'.format(round(100*average_annual_return, 2))
    result['benchmark_return'] = '{0}%'.format(round(100*benchmark_return, 2))
    if data['Interval'] == '1d':
        result['annual_benchmark_return'] = '{0}%'.format(round(100*annual_benchmark_return, 2))
    result['number_of_trade'] = num_trades
    result['winning_trades'] = winning_trades
    result['losing_trades'] = losing_trades
    result['average_profit_per_trade'] = '{0}%'.format(round(100*average_profit_per_trade, 2))
    return result
    
    



