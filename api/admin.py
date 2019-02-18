from django.contrib import admin
from api.models import Replays, Mode, Feedback, Stat


class ReplayAdmin(admin.ModelAdmin):
    list_display = ('title', 'map', 'player', 'oponent', 'processed')
    list_filter = ('map', 'player', 'oponent', 'processed')

class ModeAdmin(admin.ModelAdmin):
    list_display = ('title', 'load','map', 'player', 'oponent', 'is_enabled', 'difficulty_player',
    'difficulty_opponent', 'bot_player', 'bot_oponent')

class StatAdmin(admin.ModelAdmin):
    list_display = ('version', 'difficulty', 'name', 'result')
    list_filter = ('version', 'difficulty', 'name', 'result')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title','processed')
    list_filter = ('processed',)

admin.site.register(Replays, ReplayAdmin)
admin.site.register(Mode, ModeAdmin)
admin.site.register(Stat, StatAdmin)
admin.site.register(Feedback, FeedbackAdmin)
