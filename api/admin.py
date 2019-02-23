import os
import shutil
import base64

from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from api.models import Replays, Mode, Feedback, Stat


def download_replays(modeladmin, request, queryset):
    filenames = []
    temp_folder = settings.BASE_DIR + "/tmp"
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
    for stat in queryset.all():
        replay = Feedback.objects.get(title=stat.name)
        file_name = "{}/{}".format(temp_folder, replay.title.split("/")[-1])
        filenames.append(file_name)
        replay_file = open(file_name, "wb")
        replay_file.write(base64.b64decode(replay.base64_file))
        replay_file.close()

    file_name = "SC2Replays"
    files_path = temp_folder + "/"
    path_to_zip = shutil.make_archive(files_path, "zip", files_path)
    response = HttpResponse(FileWrapper(open(path_to_zip, 'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="{filename}.zip"'.format(
        filename=file_name.replace(" ", "_")
    )
    shutil.rmtree(temp_folder)
    return response


download_replays.short_description = "Download replays"


class ReplayAdmin(admin.ModelAdmin):
    list_display = ('title', 'map', 'player', 'oponent', 'processed')
    list_filter = ('map', 'player', 'oponent', 'processed')

class ModeAdmin(admin.ModelAdmin):
    list_display = ('title', 'load','map', 'player', 'oponent', 'is_enabled', 'difficulty_player',
    'difficulty_opponent', 'bot_player', 'bot_oponent')

class StatAdmin(admin.ModelAdmin):
    list_display = ('version', 'bot_player', 'data_source', 'difficulty', 'result')
    list_filter = ('version', 'difficulty', 'bot_player', 'result')
    actions = [download_replays]

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title','processed')
    list_filter = ('processed',)

admin.site.register(Replays, ReplayAdmin)
admin.site.register(Mode, ModeAdmin)
admin.site.register(Stat, StatAdmin)
admin.site.register(Feedback, FeedbackAdmin)
