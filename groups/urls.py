from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('create/', views.create_group_view, name='create'),
    path('list/', views.group_list_view, name='list'),
    path('<int:group_id>/', views.group_detail_view, name='detail'),
    path('<int:group_id>/add-member/', views.add_member_view, name='add_member'),
    path('<int:group_id>/remove-member/<int:member_id>/', views.remove_member_view, name='remove_member'),
    path('<int:group_id>/delete/', views.delete_group_view, name='delete'),
    path('delete/<int:group_id>/', views.delete_group_view, name='delete'),
]