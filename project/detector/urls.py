from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^poll_face_detector_state/$', views.poll_face_detector_state, name='poll_face_detector_state')
]
