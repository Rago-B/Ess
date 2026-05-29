from django.contrib import admin
from django.urls import path, include  # <--- Make sure 'path' and 'include' are here
from django.views.generic import RedirectView
import os

urlpatterns = [
    path('',include('apps.core_management.urls')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('apps.authentication.urls')),
    path('', include('apps.mail_client.urls')),
    path('employee/', include('apps.employee_portal.urls')),
    path('', include('apps.visitor_management.urls')),
    path('',include('apps.Rfid_system.urls')),
    path('',include('apps.office_logistics.urls')),
    path('',include('apps.operations_planning.urls')),
    path('',include('apps.task_management.urls')),
    path('',include('apps.bgv_system.urls')),
    path('personal-information/',include('apps.personal_information.urls')),
    

    

]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    # Use settings.BASE_DIR instead of just BASE_DIR
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'staticfiles'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
