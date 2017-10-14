from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^poll_hog_state/$', views.poll_hog_state, name='poll_hog_state')
]
