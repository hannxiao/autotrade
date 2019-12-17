from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('theories/', views.TheoryListView.as_view(), name='theories'),
    path('theories/<int:pk>', views.TheoryDetailView.as_view(), name='theory-detail'),
    path('indicators/', views.IndicatorListView.as_view(), name='indicators'),
    path('indicators/<int:pk>', views.IndicatorDetailView.as_view(), name='indicator-detail'),
    path('strategies/', views.StrategyListView.as_view(), name='strategies'),
    path('strategies/<int:pk>', views.StrategyDetailView.as_view(), name='strategy-detail'),
    path('develop/', views.Develop, name='develop'),
    path('methods/', views.Method, name='methods'),
    path('methods/get-data', views.GetData, name='get-data'),
    path('methods/get-method-arg', views.GetMethodArg, name='get-method-arg'),
    path('methods/use-method', views.UseMethod, name='use-method')
]