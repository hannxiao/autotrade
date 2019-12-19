from django import forms
import inspect

class GetDataForm(forms.Form):
    symbol = forms.CharField(help_text="Enter a valid stock symbol", initial='goog')
    start = forms.DateField(help_text="Enter a start date", initial='2011-09-01')
    end = forms.DateField(help_text="Enter an end date", initial='2012-09-09')
    
    INTERVALS = (
        ('1m', '1 minutes'),
        ('2m', '2 minutes'),
        ('5m', '5 minutes'),
        ('15m', '15 minutes'),
        ('30m', '30 minutes'),
        ('60m', '60 minutes'),
        ('90m', '90 minutes'),
        ('1d', '1 day'),
        ('1wk', '1 week'),
        ('1mo', '1 month'),
        ('3mo', '3 months'),
    )
    interval = forms.ChoiceField(choices=INTERVALS, initial='1d', help_text='Select an interval')  

class SelectIndicatorForm(forms.Form):
    from .methods import indicators 
    INDICATORS = [(ele[0], ele[0]) for ele in inspect.getmembers(indicators, inspect.isfunction)]
    indicator = forms.ChoiceField(choices=INDICATORS, help_text='Select an indicator')  
    
class SelectStrategyForm(forms.Form):
    from .methods import strategies 
    STRATEGIES = [(ele[0], ele[0]) for ele in inspect.getmembers(strategies, inspect.isfunction)]
    strategy = forms.ChoiceField(choices=STRATEGIES, help_text='Select a strategy')      
    
class SelectAnalysisForm(forms.Form):
    from .methods import analysis 
    ANALYSIS = [(ele[0], ele[0]) for ele in inspect.getmembers(analysis, inspect.isfunction)]
    analysis = forms.ChoiceField(choices=ANALYSIS, help_text='Select an analysis')   
    
class DevelopInitialForm(forms.Form):
    start = forms.DateField(initial='2011-09-01')
    end = forms.DateField(initial='2012-09-09')
    INTERVALS = (
        ('1m', '1 minutes'),
        ('2m', '2 minutes'),
        ('5m', '5 minutes'),
        ('15m', '15 minutes'),
        ('30m', '30 minutes'),
        ('60m', '60 minutes'),
        ('90m', '90 minutes'),
        ('1d', '1 day'),
        ('1wk', '1 week'),
        ('1mo', '1 month'),
        ('3mo', '3 months'),
    )
    interval = forms.ChoiceField(choices=INTERVALS, initial='1d')      
    
    
    