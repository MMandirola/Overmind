from django.db import models


class Replays(models.Model):
    title = models.CharField(max_length=200, primary_key=True)
    base64_file = models.TextField()
    extra = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    processed = models.BooleanField(default=False)
    player = models.CharField(max_length=200)
    oponent = models.CharField(max_length=200)
    map = models.CharField(max_length=200)

    def __str__(self):
        return (self.title)

    def toDict(self):
        return {
            "title": self.title,
            "base64": self.base64_file,
        }

class Mode(models.Model):
    title = models.CharField(max_length=200)
    load = models.IntegerField(default=1)
    player = models.CharField(max_length=200, null=True, blank=True)
    oponent = models.CharField(max_length=200, null=True, blank=True)
    map = models.CharField(max_length=200, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    difficulty_player = models.CharField(max_length=200, null=True, blank=True)
    difficulty_opponent = models.CharField(max_length=200, null=True, blank=True)
    bot_player = models.CharField(max_length=200, null=True, blank=True)
    bot_oponent = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return (self.title)
