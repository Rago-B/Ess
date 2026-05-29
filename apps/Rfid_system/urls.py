from django.urls import path
from . import views


urlpatterns = [
    path('Rfid-dashboard/',views.rfid,name="rfid"),
    path('gate-activity/',views.gate_activity,name="gateactivity")
]