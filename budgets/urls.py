from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('group/<int:group_id>/', views.budget_list_view, name='list'),
    path('detail/<int:budget_id>/', views.budget_detail_view, name='detail'),
    path('create/<int:group_id>/', views.create_budget_view, name='create'),
]
