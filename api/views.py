from django.shortcuts import render
import base64
from api.models import Replays, Mode
from django.conf import settings
import random
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from django.core.serializers import serialize
import json
from pymongo import MongoClient
import pymongo
# Folder where to store replay files
REPLAYS_DIR = settings.REPLAYS_DIR

client = MongoClient()
mongo_db = client.sc2
db_observations = mongo_db.observations

def mode(request):
    if request.method == "GET":
        total = 0
        probs = []
        modes = Mode.objects.filter(is_enabled=True)
        for mode in modes:
            total += mode.load
            probs.append(mode.load)
        probs = list(map(lambda x: x / total, probs))
        choice = np.random.choice(modes, 1, probs)
        return HttpResponse(serialize('json',choice))

        
    else:
        return HttpResponseNotFound("Not Found")
def replays(request):
    player = request.GET.get("player", "")
    oponent = request.GET.get("oponent", "")
    map = request.GET.get("map", "")
    keyargs = {}
    if(player):
        keyargs["player"] = player
    if oponent:
        keyargs["oponent"] = oponent
    if map:
        keyargs["map"] = map
    keyargs["processed"] = False
    replays = Replays.objects.filter(**keyargs)[:100]
    if replays:
        return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
    else:
        return HttpResponseNotFound("No replays")
        
def replays_classify(request):
    replays = Replays.objects.filter(
        processed=False, player="", oponent="")[:100]
    if replays:
        return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
    else:
        return HttpResponseNotFound("No replays")


@csrf_exempt
def classify(request):
    if request.method == "POST":
        id = request.POST.get("id")
        player = request.POST.get("player")
        opponent = request.POST.get("opponent")
        map = request.POST.get("map")

        replays = Replays.objects.filter(
            processed=False, title=id, player="", oponent="")
        if replays:
            replay = replays[0]
            replay.player = player
            replay.oponent = opponent
            replay.map = map
            replay.save()
            return HttpResponse()
    return HttpResponseNotFound()

def dict_compare(d1, d2, ignored_keys):
    return {k:v for k,v in d1.items() if k not in ignored_keys} == {k:v for k,v in d2.items() if k not in ignored_keys}
@csrf_exempt
def proccess(request):
    ignored_keys = ["games", "wins", "looses"]
    if request.method == "POST":
        observations = request.POST.get("observations")
        observations = json.loads(observations)
        for observation in observations:
            db_obs = db_observations.find_one({
                "observation":observation["observation"]
            })
            if not db_obs:
                db_observations.insert_one(observation)
            else:
                for action in db_obs["actions"]:
                    matching_actions = list(filter(lambda x: dict_compare(x, action, ignored_keys), observation["actions"]))
                    if len(matching_actions):
                        action["wins"] += matching_actions[0]["wins"]
                        action["looses"] += matching_actions[0]["looses"]
                        action["games"] += matching_actions[0]["games"]
                for action in observation["actions"]:
                    matching_actions = list(filter(lambda x: dict_compare(x, action, ignored_keys), db_obs["actions"]))
                    if not matching_actions:
                        db_obs["actions"].append(action)
                db_obs["wins"] += observation["wins"]
                db_obs["looses"] += observation["looses"]
                db_obs["games"] += observation["games"]
                db_observations.replace_one({
                "observation":observation["observation"],
                }, db_obs)                

        return HttpResponse()
    else:
        return HttpResponseNotFound()

@csrf_exempt
def finish(request):
    if request.method == "POST":
        id = request.POST.get("id")
        Replays.objects.filter(title=id).update(processed=True)
        return HttpResponse()
    else:
        return HttpResponseNotFound()

@csrf_exempt
def mark_misversion(request):
    if request.method == "POST":
        id = request.POST.get("id")
        Replays.objects.filter(title=id).update(processed=True)
        return HttpResponse()
    else:
        return HttpResponseNotFound()

def sample(request):
    if request.method == "GET":
        n = request.GET.get("n", 7000)
        observations = db_observations.aggregate([ { "$sample": { "size": n } } ], {"allowDiskUse": True})
        return JsonResponse(observations)
    else:
        return HttpResponseNotFound

