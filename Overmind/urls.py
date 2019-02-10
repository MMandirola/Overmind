from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from api import views


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^replays/classify', views.replays_classify),
    url(r'^replays/', views.replays),
    url(r'^classify/', views.classify),
    url(r'^mode/', views.mode),
    url(r'^proccess/finish', views.finish),
    url(r'^proccess/', views.proccess),
    url(r'^missversion/', views.mark_misversion)
]
