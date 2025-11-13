"""
URL configuration for spliteaseproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import dashboard_view
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('users/', include('users.urls')),
    path('expenses/', include('expenses.urls')),
    path('groups/', include('groups.urls')),
    path('settlements/', include('settlements.urls')),
    path('activities/', include('activities.urls')),
    path('chat/', include('chat.urls')),
    path('budgets/', include('budgets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "SplitEase Administration"
admin.site.site_title = "SplitEase Admin"
admin.site.index_title = "Welcome to SplitEase"
