from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def search(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        body = json.loads(request.body)
        text = body.get('search')
        if not text:
            return JsonResponse({"error": "Search term is required"}, status=400)
        with connections['external'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            names = []
            for table in tables:
                names.append(table[0])
        return JsonResponse({"names": names}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
