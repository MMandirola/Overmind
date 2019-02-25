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
    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            dest='grouped',
            help='Generate file with grouped observations only',
        )
        parser.add_argument(
            '--filename',
            dest='filename',
            help='Specify file name',
        )

    def handle(self, *args, **options):
        file_name = options.get('filename') if options.get('filename') is not None else 'observations'
        client = MongoClient()
        mongo_db = client.sc2
        db_observations = mongo_db.observations
        observations = []
        obs_file = open("static/{}.json".format(file_name), "w")
        for i in range(0,180):
            print(i)
            time.sleep(0.5)
            loop_query = {
                "$gte": i * 240,
                "$lt": (i + 1) * 240
            }
            if options.get('grouped'):
                match_query = {"$match": {"observation.loop": loop_query, "games": {"$gte": 2}}}
            else:
                match_query = {"$match": {"observation.loop": loop_query}}
            pipeline = [
                match_query,
                {"$sort": {"observation.games": -1}},
                {"$limit": 200}
            ]
            observations += db_observations.aggregate(pipeline, allowDiskUse=True)
        print("Writing to file {}.json".format(file_name))
        obs_file.write(dumps(observations))
        obs_file.close()
