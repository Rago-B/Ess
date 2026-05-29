from django.urls import path
from . import views


urlpatterns = [
    path('visitor-management/', views.visitor_management, name='visitormanagement'),
    path('view-visitors/',views.view_visitors,name="viewvisitors"),
    path('add-visitors/',views.add_visitor_form,name="addvisitors"),
    path('edit-visitors/',views.edit_visitors,name="editvisitors"),
    path('delete-visitors/<int:visitor_id>/', views.api_delete_visitor, name="api_delete_visitors"),
    path('refresh-form/',views.refresh_google_sheets,name="refreshform"),

]