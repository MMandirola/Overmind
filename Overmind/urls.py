from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from api import views


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.dashboard),
    url(r'^replays/classify', views.replays_classify),
    url(r'^replays/', views.replays),
    url(r'^classify/', views.classify),
    url(r'^mode/', views.mode),
    url(r'^proccess/finish', views.finish),
    url(r'^proccess/', views.proccess),
    url(r'^missversion/', views.mark_misversion),
    url(r'^sample/', views.sample),
    url(r'^stats/', views.stats),
    url(r'^player_replay/', views.player_replay),
    url(r'^feedback/finish', views.feedback_finish),
    url(r'^feedback/', views.feedback),
]
