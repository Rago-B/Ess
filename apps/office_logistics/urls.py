from django.urls import path
from . import views

urlpatterns = [
 
    path('seatallocation/', views.seat_allocation, name='seatallocation'),
    path('assetalloaction/',views.asset_allocation_view,name="assetallocation"),
    path('deleteasset/<int:asset_id>/', views.delete_asset_view, name='delete_asset'),
    path('transport/', views.vehicle_passes_view, name='vehiclepasses'),
    path('transport/revoke/<int:pass_id>/', views.revoke_pass_view, name='revoke_pass'),
    path('cafeteria/', views.cafeteria_management_view, name='cafeteria'),
    path('cafeteria/status/<int:complaint_id>/<str:new_status>/', views.update_complaint_status_view, name='update_complaint_status'),



]


