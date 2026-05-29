from django.urls import path
from . import views


urlpatterns = [
    
    path('planning/bench/', views.bench_management_view, name='bench_strength'),
    path('planning/bench/remove/<int:record_id>/', views.remove_from_bench_view, name='remove_from_bench'),
    path('planning/Travel/', views.travel_management_view, name='travel_management'),
    path('planning/delete-travel/',views.delete_travel_view,name='delete_travel'),
    path('planning/travel/delete/<int:travel_id>/', views.delete_travel_view, name='delete_travel'),
    path('planning/costmonitoring/',views.cost_monitoring_view,name='cost_monitoring'),
    path('planning/changeplans/',views.change_plans_view,name='change_plans'),
    path('planning/change-plans/delete/<int:plan_id>/', views.delete_change_plan_view, name='delete_change_plan'),
    path('planning/policy/',views.policy_hub_view,name='policy_hub'),
    path('planning/certifications/', views.certification_management_view, name='certifications'),
    path('planning/certifications/delete/<int:cert_id>/', views.delete_certification_view, name='delete_certification'),



]

    
    
    