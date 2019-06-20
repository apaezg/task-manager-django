from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('comments/', include('django_comments.urls')),
    path('', include('simple_tasks.urls')),
]
