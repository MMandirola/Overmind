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
