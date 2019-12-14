import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as ss
from . import toolFuncs


 


def EMA(data, N):
    '''  
    Calculate Exponential Moving Average
    Take every value into account
    Weight of every price decrease exponentially at a new period
    N is typically 12 or 26
    '''
    close = data['Close']
    ema = toolFuncs.EMA(close, N)
    return {'EMA': {'name': 'EMA', 'data': ema, 'position': 'main', 'type': 'line',
                    'showSymbol': False, 'smooth': True, 'lineStyle': {
                    'normal': {'width': 2, 'color': '#ffff66'}
                    }}
    }
    
def PrecedingHighLow(data, N):
    '''
    Calculate the highest and lowest price in the past N days (today not included)
    '''
    PrecedingHigh = toolFuncs.ExtremeOfPrecedingN(data['High'], N, 'high')
    PrecedingLow = toolFuncs.ExtremeOfPrecedingN(data['Low'], N, 'low')
    return {'high': {'name': '{0} time-units highest'.format(N), 'data': PrecedingHigh, 'position': 'main', 'type': 'line',
                    'showSymbol': False, 'smooth': True, 'lineStyle': {
                    'normal': {'width': 2, 'color': '#cc33ff'}
                    }},
            'low': {'name': '{0} time-units lowest'.format(N), 'data': PrecedingLow, 'position': 'main', 'type': 'line',
                    'showSymbol': False, 'smooth': True, 'lineStyle': {
                    'normal': {'width': 2, 'color': '#3366ff'}
                    }}
    }
    
def TrueRange(data):
    '''
    TR = max(high-low, high-preceding_close, preceding_close-low)
    '''
    close, high, low = data['Close'], data['High'], data['Low']
    tr = [None]
    
    for i in range(1, len(close)):
        tr.append(max(high[i] - low[i], close[i-1] - low[i], high[i] - close[i-1]))
        
    return {'tr': {'name': 'TrueRange', 'data': tr, 'position': 'bottom1', 'type': 'line',
                    'showSymbol': False, 'smooth': False, 'lineStyle': {
                    'normal': {'width': 2, 'color': '#ffff66'}
                    }}
            }
    
def N_turtle_system(data):
    '''
    39 days exponential moving average of true range
    '''
    N = [None]
    N.extend(toolFuncs.EMA(TrueRange(data)['tr']['data'][1:], 39))
    return {'N': {'name': 'N', 'data': N, 'position': 'bottom1', 'type': 'line',
                    'showSymbol': False, 'smooth': False, 'lineStyle': {
                    'normal': {'width': 2, 'color': '#ffff66'}
                    }}
            }    



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    