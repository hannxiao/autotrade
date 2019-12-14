from . import toolFuncs
    
    
    
    
    
def DefineTrend(data, K):
    '''
    Filter all the trend whose range less than K% 
    '''
    pairs = list(zip(data['Date'], data['Close']))
    is_extreme = toolFuncs.extreme_point(data['Close'], K, recognition_method='height')           
    output = [pairs[i] for i in range(len(is_extreme)) if is_extreme[i]]
    return {'DefineTrend': {'name': 'Trend', 'data': output, 'position': 'main', 'type': 'line', 
                            'lineStyle': {'normal': {'width': 3}, 'showSymbol':False}
                            }
    }
