from . import indicators, toolFuncs
import pandas as pd
import numpy as np


def Strategy_AIP(data, K):
    # automatic investment plan
    l = len(data['Close'])
    trade_signal = []
    single = 10000/(l//K+(l%K>0))
    
    n = 1
    for i in range(l):
        if i % K == 0:
            trade_signal.append((single, 'value','vary'))
            n += 1
        else:
            trade_signal.append(None)   
    
    stock_shares, asset = toolFuncs.backtest(data, trade_signal)
    output = {}    
    output['asset'] = {'name': 'return', 'data': asset, 'position': 'bottom1',
          'type': 'line'}
    #toolFuncs.MaximumDrawdown(asset)   
    output['stock_shares'] = {'name': 'position', 'data': stock_shares, 'position': 'bottom2', 'type': 'bar'}
    return output

def Strategy_AIP2(data, K):
    '''
    automatic investment plan
    Invest a certain amount of money every K period
    About 10000 cash(initial number) will be invested at the end
    '''
    l = len(data['Close'])
    single = 10000/(l//K+(l%K>0))
    infoDic1 = {'close': data['Close'], 'single': single}
    @toolFuncs.OrderTypeEntry   
    def entry(infoDic, asset, orders, i):
        if i == 0:
            return {'amount': infoDic['single'],
                    'amount_type': 'value', 'change_type': 'set',
                    'order_price': infoDic['close'][i]} 
            
    infoDic2 = {'close': data['Close'], 'single': single, 'K': K}
    @toolFuncs.OrderTypeSize
    def size(infoDic, asset, orders, i):
        if i != 0 and i % infoDic['K'] == 0:
            return {'amount': infoDic['single'],
                    'amount_type': 'value', 'change_type': 'vary',
                    'order_price': infoDic['close'][i]}        
    
    functions = [(entry, infoDic1), (size, infoDic2)]

    return toolFuncs.GetOutput(data, functions)


def Strategy_Turtles(data):
    '''
    A trading system developed by Richard Dennis
    N: exponential average of true range, measures volatility, used to determine trading unit, level of stop price, etc.
    Richard Donchian's Channel breakout system is used here
    Entry when 20 days breakout happens(system1)
    Entry system1 is ignored when last trade exits with profit
    Entry when 55 days breakout happens(system2)
    Stop loss at 2N below the latest entry price
    Exit when the opposite 10 days breakout happens(system1)
    Exit when the opposite 20 days breakout happens(system2)
    Add unit at 1/2 N price following the entry
    Position size is controlled by N
    '''
    # calculate N
    N = [None]
    N.extend(toolFuncs.EMA(indicators.TrueRange(data)['tr']['data'][1:], 39))
    # entry system1
    PrecedingHighs20 = indicators.PrecedingHighLow(data, 20)['high']['data']
    PrecedingLows20 = indicators.PrecedingHighLow(data, 20)['low']['data'] 
    # entry system2
    PrecedingHighs55 = indicators.PrecedingHighLow(data, 55)['high']['data']
    PrecedingLows55 = indicators.PrecedingHighLow(data, 55)['low']['data']    
    # infoDic: calculated results from data

    infoDic2 = {'PrecedingHighs55': PrecedingHighs55, 'PrecedingLows55': PrecedingLows55,
                'N': N, 'high': data['High'], 'low': data['Low'], 'open': data['Open']}                              
    @toolFuncs.OrderTypeEntry   
    def entry_func2(infoDic, asset, orders, i):
        # entry condition
        if infoDic['N'][i]:                    
            # entry system2
            if infoDic['PrecedingHighs55'][i] and infoDic['high'][i] > infoDic['PrecedingHighs55'][i]:
                return {'amount': asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'set',
                        'order_price': max(infoDic['PrecedingHighs55'][i], infoDic['open'][i])}                
            if infoDic['PrecedingLows55'][i] and infoDic['low'][i] < infoDic['PrecedingLows55'][i]:
                return {'amount': -asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'set',
                        'order_price': min(infoDic['PrecedingLows55'][i], infoDic['open'][i])}                  
        return None
    
    infoDic1 = {'PrecedingHighs20': PrecedingHighs20, 'PrecedingLows20': PrecedingLows20,
                'N': N, 'high': data['High'], 'low': data['Low'], 'open': data['Open']}
    @toolFuncs.OrderTypeEntry    
    def entry_func1(infoDic, asset, orders, i):
        # entry condition
        if infoDic['N'][i] and (not orders or orders[-1]['event_type'] == 'stop_func'):
        # entry system1 condition: previous winner trade (with 'exit' other than 'stop')
        # will make it ignored
            if infoDic['PrecedingHighs20'][i] and infoDic['PrecedingHighs20'][i] < infoDic['high'][i]:
                return {'amount': asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'set',
                        'order_price': max(infoDic['PrecedingHighs20'][i], infoDic['open'][i])}
            elif infoDic['PrecedingLows20'][i] and infoDic['PrecedingLows20'][i] > infoDic['low'][i]:
                return {'amount': -asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'set',
                        'order_price': min(infoDic['PrecedingLows20'][i], infoDic['open'][i])}

    infoDic3 = {'N': N, 'open': data['Open'], 'low': data['Low'], 'high': data['High']}
    @toolFuncs.OrderTypeExit
    def stop_func(infoDic, asset, orders, i):
        if infoDic['N'][i]:
            position_direction = (asset['position'] > 0) * 2 - 1 # long: 1, short: -1
            target_price = orders[-1]['order_price'] - position_direction * 2 * infoDic['N'][i]
            if position_direction > 0 and infoDic['low'][i] < target_price:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': min(target_price, infoDic['open'][i])}
            elif position_direction < 0 and infoDic['high'][i] > target_price:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': max(target_price, infoDic['open'][i])}
        return None
    
    PrecedingHighs10 = indicators.PrecedingHighLow(data, 10)['high']['data']
    PrecedingLows10 = indicators.PrecedingHighLow(data, 10)['low']['data']  
    infoDic4 = {'PrecedingHighs20': PrecedingHighs20, 'PrecedingLows20': PrecedingLows20,
                'PrecedingHighs10': PrecedingHighs10, 'PrecedingLows10': PrecedingLows10,
                'high': data['High'], 'low': data['Low'], 'open': data['Open']}   
    @toolFuncs.OrderTypeExit
    def exit_func(infoDic, asset, orders, i):
        j = 1
        while orders[-j]['event_type'] not in {'entry_func1', 'entry_func2'}:
            j += 1
        trade_entry_type = orders[-j]['event_type']           
        if asset['position'] > 0:
            if trade_entry_type == 'entry_func1' and infoDic['PrecedingLows10'][i] and infoDic['PrecedingLows10'][i]>infoDic['low'][i]:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': min(infoDic['PrecedingLows10'][i], infoDic['open'][i])}                    
            if trade_entry_type == 'entry_func2' and infoDic['PrecedingLows20'][i] and infoDic['PrecedingLows20'][i]>infoDic['low'][i]:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': min(infoDic['PrecedingLows20'][i], infoDic['open'][i])}
        if asset['position'] < 0: 
            if trade_entry_type == 'entry_func1' and infoDic['PrecedingHighs10'][i] and infoDic['PrecedingHighs10'][i]<infoDic['high'][i]:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': max(infoDic['PrecedingHighs10'][i], infoDic['open'][i])}                    
            if trade_entry_type == 'entry_func2' and infoDic['PrecedingHighs20'][i] and infoDic['PrecedingHighs20'][i]<infoDic['high'][i]:
                return {'amount': 0, 'amount_type': 'stock',
                        'change_type': 'set', 'order_price': max(infoDic['PrecedingHighs20'][i], infoDic['open'][i])}                
        return None

    infoDic5 = {'high': data['High'], 'low': data['Low'], 'open': data['Open'], 'N': N}
    @toolFuncs.OrderTypeSize
    def size_func(infoDic, asset, orders, i):
        # add unit 
        if infoDic['N'][i] and abs(asset['position'])*infoDic['N'][i]<asset['total']*3/100:
            position_direction = (asset['position'] > 0) * 2 - 1 # long: 1, short: -1
            target_price = orders[-1]['order_price'] + position_direction * 0.5 * infoDic['N'][i]
            
            if position_direction > 0 and infoDic['high'][i] > target_price:
                return {'amount': asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'vary',
                        'order_price': max(target_price, infoDic['open'][i])} 
            elif position_direction < 0 and infoDic['low'][i] < target_price:
                return {'amount': -asset['total']/100/infoDic['N'][i],
                        'amount_type': 'stock', 'change_type': 'vary',
                        'order_price': min(target_price, infoDic['open'][i])}                 
        return None    
    
    functions = [(entry_func1, infoDic1), (entry_func2, infoDic2),
                 (stop_func, infoDic3), (exit_func, infoDic4), (size_func, infoDic5)]
    
    return toolFuncs.GetOutput(data, functions)















