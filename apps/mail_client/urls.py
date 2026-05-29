from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('fetch-email-content/', views.fetch_email_content_ajax, name='fetch_email_content'),
    path('send-email-ajax/', views.send_email_ajax, name='send_email_ajax'),
    path('delete-email-ajax/', views.delete_email_ajax, name='delete_email_ajax'),
    path('save-draft-ajax/', views.save_draft_ajax, name='save_draft_ajax'),
    path('toggle-pin-ajax/', views.toggle_pin_ajax, name='toggle_pin_ajax'),
    path('toggle-star-ajax/', views.toggle_star_ajax, name='toggle_star_ajax'),
    path('snooze-email-ajax/', views.snooze_email_ajax, name='snooze_email_ajax'),
    path('unsnooze-email-ajax/', views.unsnooze_email_ajax, name='unsnooze_email_ajax'),
    path('save-settings-ajax/', views.save_settings_ajax, name='save_settings_ajax'),
    path('move-email-ajax/', views.move_email_ajax, name='move_email_ajax'),
    path('company-policy/', views.company_policy, name='company_policy'),
]
