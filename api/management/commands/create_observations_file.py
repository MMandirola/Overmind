from django.core.management.base import BaseCommand, CommandError
from api.models import Replays
from os import listdir
from os.path import isfile, join
import base64
import os
from django.conf import settings
REPLAYS_DIR = settings.REPLAYS_DIR
from pymongo import MongoClient

class Command(BaseCommand):

    def handle(self, *args, **options):
        client = MongoClient()
        mongo_db = client.sc2
        db_observations = mongo_db.observations
        pipelines = {str(i):[
            {"$match": {"observation.loop": i * 24}},
            {"$sort": {"observation.games": -1}},
            {"$limit": 100}
        ] for i in range(0, 1800)}
        main_pipeline = [
            {"$match": {"observation.loop": {
                "$gte": 0,
                "$lt": 43200
            }}},
            {"$facet" : pipelines},
            {"$project": {"cases":{"$setUnion":["$" + str(i) for i in range(0, 1800)]}}},
            {"$unwind": "$cases"},
            {"$replaceRoot": { "newRoot": "$cases" }}
        ]
        print(main_pipeline)
        observations = db_observations.aggregate(main_pipeline, allowDiskUse=True)


