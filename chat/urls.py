from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('group/<int:group_id>/', views.group_chat_view, name='group_chat'),
    path('send/<int:group_id>/', views.send_message_view, name='send_message'),
    path('messages/<int:group_id>/', views.get_messages_view, name='get_messages'),
    path('online/<int:group_id>/', views.get_online_members_view, name='online_members'),
]
