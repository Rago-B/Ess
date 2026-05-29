from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/personal-information/', views.personal_info_dashboard_view, name='personal_info_dashboard'),
    path('dashboard/profile-photo/setup/', views.profile_photo_setup_view, name='profile_photo_setup'),
    path('dashboard/profile-photo/upload-api/', views.api_upload_profile_photo_later_view, name='api_upload_photo_later'),

    path('verification/upload-vault/', views.upload_documents_workspace_view, name='upload_docs_tab'),
    path('verification/view-vault/', views.view_documents_directory_view, name='view_docs_tab'),
    path('dashboard/passport-details/view/', views.standalone_passport_details_view, name='passport_details_standalone_view'),




    path('verification/upload/', views.upload_verification_document_api, name='upload_verification_doc'),
    path('verification/preview/<str:doc_type>/', views.preview_verification_document_view, name='preview_verification_doc'),

     path('personal-information/education-certification-vault/', views.education_certification_workspace_view,name='education_certification_workspace'),
     path('previous-employer-overview/', views.previous_employer_workspace_view, name='previous_employer_workspace'),
     path('family-details-registry/', views.family_details_workspace_view, name='family_details'),
     path('visa-details-vault/',views.visa_details_workspace_view,name='visa_details_workspace'),
     path('id-card-workspace/',views.id_card_dashboard_view,name='id_card_dashboard'),
     path('communication-overview/', views.communication_overview_view,name='communication_overview_dashboard'),
     path('payslips/', views.payslip_workspace_view, name='payslip_workspace'),



]
