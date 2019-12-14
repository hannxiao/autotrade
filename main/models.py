from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
import uuid 

class Theory(models.Model):
    """
    Model representing a trading theory.
    """
    name = models.CharField(max_length=200, help_text="Enter the name of theory")
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the theory")
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('theory-detail', args=[str(self.id)])

class Indicator(models.Model):
    """
    Model representing a indicator.
    """
    name = models.CharField(max_length=200, help_text="Enter the name of indicator")
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the indicator")
    related = models.ManyToManyField('self', blank=True) 
    
    def display_related(self):
        return ', '.join([ind.name for ind in self.related.all()])
    display_related.short_description = 'Related indicators'
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('indicator-detail', args=[str(self.id)])
    
class IndicatorInstance(models.Model):
    """
    A specific indicator.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular indicator")
    indicator = models.ForeignKey(Indicator, on_delete=models.SET_NULL, null=True)
    kwarg = models.CharField(max_length=200, help_text="Enter the dictionary containing indicator-related parameter",
                             null=True, blank=True)
    
    def __str__(self):
        if self.indicator:
            return 'Instance of ' + self.indicator.name
        return 'null'

class Strategy(models.Model):
    """
    Model representing a Strategy (may be related to indicator or theory).
    """
    name = models.CharField(max_length=200, help_text="Enter the name of strategy")
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the strategy")        
    indicator = models.ManyToManyField(Indicator, blank=True) 

    def display_indicator(self):
        return ', '.join([ind.name for ind in self.indicator.all()])
    display_indicator.short_description = 'Related indicators'  
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('strategy-detail', args=[str(self.id)])
    
class StrategyInstance(models.Model):
    """
    Model representing a Strategy (may be related to indicator or theory).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular strategy")
    strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True)
    kwarg = models.CharField(max_length=200, help_text="Enter the dictionary containing indicator-related parameter",
                             null=True, blank=True)     
    
    def __str__(self):
        if self.strategy:
            return 'Instance of ' + self.indicator.name
        return 'null'  
    
class Portfolio(models.Model):
    """
    A combination of many single stocks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular portfolio")
    weights = models.CharField(max_length=200, help_text="Enter an array that has sum = 1")   # later change it to an array container
    symbols = models.CharField(max_length=200, help_text="Enter a list of symbols")  
    
    def __str__(self):
        return self.symbols     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    