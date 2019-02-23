from django.db.models import Count
from django.shortcuts import render
import base64
from api.models import Replays, Mode, Stat, Feedback
from django.conf import settings
import random
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from django.core.serializers import serialize
import json
from pymongo import MongoClient
import pymongo
from bson.json_util import dumps

# Folder where to store replay files
REPLAYS_DIR = settings.REPLAYS_DIR

client = MongoClient()
mongo_db = client.sc22
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

def feedback(request):
    keyargs = {}
    keyargs["processed"] = False
    replays = Feedback.objects.filter(**keyargs)[:100]
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
def feedback_finish(request):
    if request.method == "POST":
        id = request.POST.get("id")
        Feedback.objects.filter(title=id).update(processed=True)
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
        n = int(request.GET.get("n", 1))
        observations = []
        for i in range(0,250):
            pipeline = [ 
                {"$match": {"observation.loop": {
                    "$gte": i * 172,
                    "$lt": (i + 1) * 172
                }}},
                { "$sample": { "size": n } } 
            ]
            print(pipeline)
            print(i)
            observations += db_observations.aggregate(
            pipeline,
            allowDiskUse=True)
        return HttpResponse(dumps(observations))
    else:
        return HttpResponseNotFound()


@csrf_exempt
def stats(request):
    if request.method == "POST":
        version = request.POST.get("version")
        difficulty = request.POST.get("difficulty")
        name = request.POST.get("name")
        data_source = request.POST.get("data_source")
        bot_player = request.POST.get("bot_player")
        result = request.POST.get("result")
        Stat.objects.create(**{
            "version": version,
            "difficulty": difficulty,
            "name": name,
            "bot_player": bot_player,
            "data_source": data_source,
            "result": result
        })
        return HttpResponse()
    else:
        return HttpResponseNotFound()


@csrf_exempt
def player_replay(request):
    if request.method == "POST":
        title = request.POST.get("title")
        base64_file = request.POST.get("base64_file")
        st = Feedback(title, base64_file)
        st.save()
        return HttpResponse()
    else:
        return HttpResponseNotFound()


def dashboard(request):
    def _format_row(row):
        completed_games = row.get('1', 0) + row.get('2', 0)
        formated_row = {
            'version': row['version'],
            'player': row['bot_player'],
            'data_source': row['data_source'],
            'difficulty': row['difficulty'],
            'interrupted': row.get('0', 0),
            'won': row.get('1', 0),
            'lost': row.get('2', 0),
            'games': row.get('0', 0) + row.get('1', 0) + row.get('2', 0),
            'winrate': row.get('1', 0) / completed_games if completed_games else 'N/A',
        }
        return formated_row

    data = dashboard_data()
    formated_data = list(map(_format_row, data))
    formated_data.sort()
    return render(request, 'index.html', context={
        "data": formated_data,
        "games_played": Stat.objects.count(),
        "observations": db_observations.count(),
    })


def dashboard_data():
    grouped_stats = Stat.objects.values('version', 'bot_player', 'difficulty', 'data_source', 'result').annotate(count_stats=Count('result'))
    data = {}
    for stat in grouped_stats:
        key = str(stat['version']) + str(stat['bot_player']) + str(stat['difficulty']) + str(stat['data_source'])
        data.setdefault(key, {})[stat['result']] = stat.pop('count_stats')
        stat.pop('result')
        data[key].update(stat)
    return data.values()
