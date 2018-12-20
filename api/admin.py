from django.contrib import admin
from api.models import Replays


class ReplayAdmin(admin.ModelAdmin):
    list_display = ('title', 'map', 'player', 'oponent', 'processed')
    list_filter = ('map', 'player', 'oponent', 'processed')


admin.site.register(Replays, ReplayAdmin)
