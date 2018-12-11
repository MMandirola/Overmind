from django.core.management.base import BaseCommand, CommandError
from api.models import Replays
from os import listdir
from os.path import isfile, join
import base64
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        onlyfiles = [f for f in listdir("Replays")]
        if len(onlyfiles) > 200:
            onlyfiles = onlyfiles[:200]
        for file in onlyfiles:
            if(len(Replays.objects.filter(title=file))):
                os.remove("Replays/" + file)
                continue
            with open("Replays/" + file, "rb") as replay:
                encoded_string = base64.b64encode(replay.read())
                replay = Replays(title=file, base64_file=encoded_string)
                replay.save()
