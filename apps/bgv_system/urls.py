# Inside apps/core_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
        path('bgv/', views.bgv_dashboard_view, name='bgvdashboard'),
        path('management/bgv-officer/desk/', views.bgv_officer_dashboard, name='bgv_officer_desk'),
        path("upload-documents/", views.upload_documents, name="upload_documents"),
        path("bgv/send/<str:submission_id>/", views.send_to_bgv, name="send_to_bgv"),
        path("bgv/officer/offer/<path:submission_id>/", views.generate_offer_letter_pdf_view, name="generate_offer_letter"),
        path("bgv/officer/verify/<str:submission_id>/", views.verify_candidate, name="verify_candidate"),





]
