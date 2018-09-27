from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from api.views import ReplaysResource

replays_resources = ReplaysResource()

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/', include(replays_resources.urls)),
]