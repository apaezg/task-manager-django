from django.urls import path
from simple_tasks import views

urlpatterns = [
    path('', views.TaskList.as_view(), name='task_list'),
    path('task/<int:pk>', views.TaskDetail.as_view(), name='task_detail'),
    path('create', views.TaskCreate.as_view(), name='task_create'),
    path('update/<int:pk>', views.TaskUpdate.as_view(), name='task_update'),
    path('archive/<int:pk>', views.TaskArchive.as_view(), name='task_archive'),
]
