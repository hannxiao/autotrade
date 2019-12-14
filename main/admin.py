from django.contrib import admin

# Register your models here.
from .models import Theory, Indicator, Strategy, IndicatorInstance, StrategyInstance, Portfolio

# =============================================================================
# admin.site.register(Theory)
# admin.site.register(Indicator)
# admin.site.register(Strategy)
# =============================================================================

@admin.register(Theory)
class TheoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_related')
    
    fieldsets = (
        (None, {
            'fields': ('name','summary')
        }),
        ('Other', {
            'fields': ['related']
        }),
    )    

    
@admin.register(Strategy) 
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_indicator')  
    
    fieldsets = (
        (None, {
            'fields': ('name','summary')
        }),
        ('Other', {
            'fields': ['indicator']
        }),
    )
    
admin.site.register(IndicatorInstance)
admin.site.register(StrategyInstance)
admin.site.register(Portfolio)    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    