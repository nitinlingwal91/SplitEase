from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('add/<int:group_id>/', views.add_expense_view, name='add'),
    path('list/<int:group_id>/', views.expense_list_view, name='list'),
    path('detail/<int:expense_id>/', views.expense_detail_view, name='detail'),
    path('edit/<int:expense_id>/', views.edit_expense_view, name='edit'),
    path('delete/<int:expense_id>/', views.delete_expense_view, name='delete'),
]
