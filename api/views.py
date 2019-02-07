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
    if(player):
        if(oponent):
            replays = Replays.objects.filter(
                processed=False, player=player, oponent=oponent)[:1000]
            if replays:
                return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
            else:
                return HttpResponseNotFound("No replays")
        else:
            replays = Replays.objects.filter(
                processed=False, player=player)[:1000]
            if replays:
                return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
            else:
                return HttpResponseNotFound("No replays")
    else:
        if(oponent):
            replays = Replays.objects.filter(
                processed=False, oponent=oponent)[:1000]
            if replays:
                return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
            else:
                return HttpResponseNotFound("No replays")
        else:
            replays = Replays.objects.filter(
                processed=False)[:1000]
            if(replays):
                return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
            else:
                return HttpResponseNotFound("No replays")


def replays_classify(request):
    replays = Replays.objects.filter(
        processed=False, player="", oponent="")[:1000]
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

@csrf_exempt
def proccess(request):
    if request.method == "POST":
        id = request.POST.get("id")
        observations = request.POST.get("observations")
        observations = json.loads(observations)
        for observation in observations:
            db_obs = db_observations.find_one({
                "observation":observation["observation"],
                "mapMetadata": observation["mapMetadata"]
                }
            )
            if not db_obs:
                db_observations.insert_one({
                    "observation": observation["observation"],
                    "mapMetadata": observation["mapMetadata"],
                    "metadata": {
                        "playerId": observation["metadata"]["playerId"],
                        "races": observation["metadata"]["races"],
                        "map": observation["metadata"]["map"]
                    },
                    "replays": [id],
                    "actions": [
                        {
                            "action": action,
                            "wins": 1 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 0,
                            "looses": 0 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 1,
                            "games": 1
                            
                        } for action in observation["actions"]
                    ]
                })
            else:
                if id not in db_obs["replays"]:
                    db_obs["replays"].append(id)
                    for action in db_obs["actions"]:
                        if action["action"] in observation["actions"]:
                            action["wins"] += (1 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 0)
                            action["looses"] += (0 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 1)
                            action["games"] += 1
                    for action in observation["actions"]:
                        if action not in map(lambda x : x["action"], db_obs["actions"]):
                            db_obs["actions"].append(
                                {
                                    "action": action,
                                    "wins": 1 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 0,
                                    "looses": 0 if observation["metadata"]["results"][(observation["metadata"]["playerId"]) - 1] == 1 else 1,
                                    "games": 1
                                },
                            )
                    db_observations.replace_one({
                    "observation":observation["observation"],
                    "mapMetadata": observation["mapMetadata"]
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

