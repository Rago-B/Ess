# Open apps/task_manager/urls.py and paste this clean router mapping configuration:

from django.urls import path
from . import views

urlpatterns = [
    
    path('tasks/my-tasks/', views.my_tasks_view, name='my_tasks'),

    path('tasks/board/', views.task_board_view, name='task_board'),
    path('tasks/assign/', views.assign_task_view, name='assign_task'),
    path('tasks/create/', views.add_task_creation_view, name='add_task_form'),

    
    path('tasks/my-tasks/update/<int:task_id>/', views.update_task_status_view, name='update_task_status'),
]
