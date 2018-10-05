from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from api.views import ReplaysResource
from api.views import store_rules

replays_resources = ReplaysResource()

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/', include(replays_resources.urls)),
    url(r'^rule/', store_rules)
]