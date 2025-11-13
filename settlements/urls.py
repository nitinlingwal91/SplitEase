from django.urls import path
from . import views

app_name = 'settlements'

urlpatterns = [
    path('balance/', views.balance_summary_view, name='balance_summary'),
    path('balance/<int:group_id>/', views.group_balance_view, name='group_balance'),
    path('optimize/<int:group_id>/', views.optimize_settlements_view, name='optimize'),
    path('list/<int:group_id>/', views.settlement_list_view, name='settlement_list'),
    path('complete/<int:settlement_id>/', views.mark_settlement_complete_view, name='mark_complete'),
]
