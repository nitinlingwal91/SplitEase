from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('feed/<int:group_id>/', views.activity_feed_view, name='feed'),
]
