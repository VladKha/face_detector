from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('project.detector.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
