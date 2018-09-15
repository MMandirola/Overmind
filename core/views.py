from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Question

@csrf_exempt
def traeme(request):
    if request.method == "GET":
        questions = list(Question.objects.filter(question_text="En que anda la banda ?"))
        response = list(map(lambda x : str(x), questions))
        return JsonResponse({"questions": response})
    if request.method == "POST":
        Question.objects.create(
            question_text = request.POST["question_text"],
            pub_date = request.POST["date"]
        )
        return JsonResponse({"status":"success"})
