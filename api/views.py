from django.shortcuts import render
import base64
from api.models import Replays
from django.conf import settings
import random
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Folder where to store replay files
REPLAYS_DIR = settings.REPLAYS_DIR


def replays(request):
    player = request.GET.get("player", "")
    oponent = request.GET.get("oponent", "")
    if(player):
        if(oponent):
            replays = Replays.objects.filter(
                processed=False, player=player, oponent=oponent)[:1000]
            return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
        else:
            replays = Replays.objects.filter(
                processed=False, player=player)[:1000]
            return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
    else:
        if(oponent):
            replays = Replays.objects.filter(
                processed=False, oponent=oponent)[:1000]
            return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())
        else:
            replays = Replays.objects.filter(
                processed=False)[:1000]
            return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())


def replays_classify(request):
    replays = Replays.objects.filter(
        processed=False, player="", oponent="")[:1000]
    return JsonResponse(replays[random.randint(0, len(replays) - 1)].toDict())


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
