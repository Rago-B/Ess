from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.auth_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('inbox-login-ajax/', views.inbox_login_ajax, name='inbox_login_ajax'),
    path('verify-otp-ajax/', views.verify_otp_ajax, name='verify_otp_ajax'),
    path('logout/', views.logout_view, name='logout'),
    # path('selected-canditates-login',views.selected_canditate_view,name="selected_canditate_view"),
   
    
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/candidate-callback/', views.google_callback, name='google_callback'),
    # path('upload-documents/', views.candidate_onboarding_workspace_view, name='upload_documents'),
    path('Welcome/', views.welcome_board, name='welcome_board'),
    path('cadidate_form/', views.candidate_personal_info_form_view, name='candidate_form'),

]
