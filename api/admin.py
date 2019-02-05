from django.contrib import admin
from api.models import Replays, Mode


class ReplayAdmin(admin.ModelAdmin):
    list_display = ('title', 'map', 'player', 'oponent', 'processed')
    list_filter = ('map', 'player', 'oponent', 'processed')

class ModeAdmin(admin.ModelAdmin):
    list_display = ('title', 'load','map', 'player', 'oponent', 'is_enabled', 'difficulty_player',
    'difficulty_opponent', 'bot_player', 'bot_oponent')

admin.site.register(Replays, ReplayAdmin)
admin.site.register(Mode, ModeAdmin)
