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
        mongo_db = client.sc22
        db_observations = mongo_db.observations
        obs_file = open("static/{}.json".format(file_name), "w")
        obs_file.write("[")
        max_iter = 180
        for i in range(0, max_iter):
            print(i)
            time.sleep(0.5)
            if options.get('grouped'):
                match_query = {"$match": {"observation.loop": 240 * i, "games": {"$gte": 2}}}
            else:
                match_query = {"$match": {"observation.loop": 240 * i}}
            pipeline = [
                match_query,
                {"$sort": {"observation.games": -1}},
                {"$limit": 200}
            ]
            print("Writing chunk {}".format(i))
            obs_file.write(dumps(db_observations.aggregate(pipeline, allowDiskUse=True))[1:-1])
            if i < (max_iter - 1):
                obs_file.write(",")
        print("Finishing file {}.json".format(file_name))
        obs_file.write("]")
        obs_file.close()
