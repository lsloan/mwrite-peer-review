from django.conf.urls import url
from . import views

app_name = 'lti'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^config/', views.ConfigView.as_view(), name='config'),
    url(r'^launch/', views.LaunchView.as_view(), name='launch'),
    url(r'^return/', views.ReturnView.as_view(), name='return'),
]
