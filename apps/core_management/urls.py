# Inside apps/core_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admin/users/', views.user_management_view, name='user_management'),
    path('admin/users/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('directory/employee/json/<int:employee_id>/', views.employee_ajax_detail_view, name='employee_json_detail'),
    path('directory/employees/', views.consolidated_employees_view, name='employee_directory'),
    path('directory/employees/update/<int:employee_id>/', views.update_employee_profile_view, name='update_employee'),
    path('planning/clients/', views.client_management_view, name='client_management'),
    path('planning/product-clients/', views.product_clients_view, name='product_clients'),
    path('planning/product-clients/delete/<int:record_id>/', views.delete_product_client_view, name='delete_product_client'),
]
