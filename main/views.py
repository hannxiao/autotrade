from .models import Theory, Indicator, Strategy
from django.views import generic
from .methods import functions, indicators, strategies, analysis, toolFuncs

from django.http import JsonResponse
import inspect
from django.shortcuts import render
import json

from .forms import *

def index(request):
    return render(
        request,
        'index.html',
    )
    
class TheoryListView(generic.ListView):
    model = Theory
    
class TheoryDetailView(generic.DetailView):
    model = Theory
    
class IndicatorListView(generic.ListView):
    model = Indicator
    
class IndicatorDetailView(generic.DetailView):
    model = Indicator

class StrategyListView(generic.ListView):
    model = Strategy
    
class StrategyDetailView(generic.DetailView):
    model = Strategy
    
def Develop(request):
    developInitialForm = DevelopInitialForm()
    selectStrategyForm = SelectStrategyForm()
    return render(
        request,
        'develop.html',
        {'developInitialForm': developInitialForm,
         'selectStrategyForm': selectStrategyForm, 
                 }
    )

def Method(request):
    getDataForm = GetDataForm()
    selectIndicatorForm = SelectIndicatorForm()
    selectStrategyForm = SelectStrategyForm()
    selectAnalysisForm = SelectAnalysisForm()
    
    return render(
        request,
        'methods.html',
        {'getDataForm': getDataForm, 
         'selectIndicatorForm': selectIndicatorForm,
         'selectStrategyForm': selectStrategyForm, 
         'selectAnalysisForm': selectAnalysisForm, 
         }
    )
    
   
def GetData(request):
    requestDic = json.loads(request.body)    
    symbol = requestDic.get('symbol', None)    
    start = requestDic.get('start', None) 
    end = requestDic.get('end', None)    
    interval = requestDic.get('interval', None) 
    
    if symbol and start and end and interval:
        stock = functions.Generic(symbol, start, end, interval)
        data = stock._data 
        new_data = dict(data.reset_index())
        for ele in new_data:
           new_data[ele] = list(new_data[ele])
        return JsonResponse(new_data)
    else:
        return JsonResponse({'symbol':symbol, 'start':start, 'end':end, 'interval':interval})

    stock = functions.Generic(symbol, start, end, interval)    
    data = stock._data 
    new_data = dict(data.reset_index())
    for ele in new_data:
       new_data[ele] = list(new_data[ele])
    
    return JsonResponse(new_data)
    
def GetMethodArg(request):
    Name = request.POST.get('name', None)
    Type = request.POST.get('type', None) 
    
    if Type == 'indicator':
        lib = indicators
    elif Type == 'strategy':
        lib = strategies
    else:
        lib = analysis
        
    for ind in inspect.getmembers(lib, inspect.isfunction):
        if ind[0] == Name:
            arg = ind[1].__code__.co_varnames[:ind[1].__code__.co_argcount]
            arg = [ele for ele in arg if ele!='data']  #remove the input 'data'
            helpText = ind[1].__doc__
            if helpText:
                helpText = [line.strip() for line in helpText.strip().splitlines()]
            # remove useless spaces, split by line 

            return JsonResponse({'arg': arg, 'helpText': helpText})
    
def UseMethod(request):
    requestDic = json.loads(request.body)
    Name = requestDic.get('name', None)
    Type = requestDic.get('type', None)

    if Type == 'indicator':
        lib = indicators
    elif Type == 'strategy':
        lib = strategies
    else:
        lib = analysis

    data = {}
    data['Open'] = requestDic.get('Open', None) 
    data['Close'] = requestDic.get('Close', None)  
    data['High'] = requestDic.get('High', None)  
    data['Low'] = requestDic.get('Low', None)  
    data['Volume'] = requestDic.get('Volume', None)  
    data['Date'] = requestDic.get('Date', None)  

    kwargs = {'data': data}    
    keys = requestDic.keys() - {'name', 'type', 'Open', 'Close', 'High', 
                           'Low', 'Volume', 'Date', 'Adj Close', 'Amount'}
    for key in keys:
        kwargs[key] = eval(requestDic.get(key, None))
                
    for ind in inspect.getmembers(lib, inspect.isfunction):
        if ind[0] == Name:
            output = ind[1](**kwargs)
            return JsonResponse(output)
    
def AnalyzeStrategy(request):
    requestDic = json.loads(request.body)
    Name = requestDic.get('name', None)    
    
    data = {}
    data['Open'] = requestDic.get('Open', None) 
    data['Close'] = requestDic.get('Close', None)  
    data['High'] = requestDic.get('High', None)  
    data['Low'] = requestDic.get('Low', None)  
    data['Volume'] = requestDic.get('Volume', None)  
    data['Date'] = requestDic.get('Date', None)
    
    kwargs = {'data': data}    
    keys = requestDic.keys() - {'name', 'interval', 'symbol', 'Open', 'Close', 'High', 
                           'Low', 'Volume', 'Date', 'Adj Close', 'Amount'}    
    
    for key in keys:
        kwargs[key] = eval(requestDic.get(key, None))
        
    for ind in inspect.getmembers(strategies, inspect.isfunction):
        if ind[0] == Name:
            output = ind[1](**kwargs)
            
            equity = output['equity']['data']
            positions = output['positions']['data']
            ordersData = output['ordersData']['data']
            
            data['Interval'] = requestDic.get('interval', None)
            data['Symbol'] = requestDic.get('symbol', None)            
            result = toolFuncs.StrategyAnalyses(data, equity, positions, ordersData)
            return JsonResponse(result)
        
        
        
    