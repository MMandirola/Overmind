from django.core.management.base import BaseCommand, CommandError
from api.models import Replays
from os import listdir
from os.path import isfile, join
import base64
import os
from django.conf import settings
REPLAYS_DIR = settings.REPLAYS_DIR
from pymongo import MongoClient
import itertools
import time
from bson.json_util import dumps

class Command(BaseCommand):

    def handle(self, *args, **options):
        client = MongoClient()
        mongo_db = client.sc2
        db_observations = mongo_db.observations
        observations = []
        obs_file = open("observations.json", "w")
        for i in range(0,1800):
            print(i)
            time.sleep(0.5)
            pipeline = [
                {"$match": {"observation.loop": i * 24}},
                {"$sort": {"observation.games": -1}},
                {"$limit": 10}
            ]
            observations += db_observations.aggregate(pipeline, allowDiskUse=True)
        obs_file.write(dumps(observations))
        
