from django.shortcuts import render
import base64
from tastypie.resources import ModelResource
from api.models import Replays
from tastypie.authorization import Authorization
from django.conf import settings
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

# Folder where to store replay files
REPLAYS_DIR = settings.REPLAYS_DIR

class ReplaysResource(ModelResource):
    class Meta:
        queryset = Replays.objects.all()
        resource_name = 'replays'
        authorization = Authorization()
        fields = ['title', 'base64_file', 'date'] # Limiting fields

    # obj_create override, in order to do something when on POST
    def obj_create(self,bundle,**kwargs):
        bundle = super(ReplaysResource,self).obj_create(bundle,**kwargs)

        # Save recieved base64 encoded file
        request_base64_file = bundle.data['base64_file']
        request_title = bundle.data['title']
        fullpath = REPLAYS_DIR + request_title
        replay_file = open(fullpath, "wb")
        replay_file.write(base64.b64decode(request_base64_file))
        replay_file.close()

        return bundle
@csrf_exempt
def store_rules(request):
    #Step 1: Connect to MongoDB - Note: Change connection string as needed
    client = MongoClient('localhost:27017')
    db=client.business
    #Step 2: Insert in the collection
    if request.method == 'GET':
        return HttpResponse("Ok")
    elif request.method == 'POST':
        print(request.body)
        result = db.reviews.insert_one(json.loads(request.body))
        return HttpResponse("Ok")