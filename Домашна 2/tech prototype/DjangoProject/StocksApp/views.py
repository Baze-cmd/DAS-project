from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def homepage(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only get method is allowed"}, status=405)
    with connections['external'].cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 8")
        tables = cursor.fetchall()
        front_page = []
        for table in tables:
            front_page.append(table[0])
        return JsonResponse({"front_page": front_page}, status=200)


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
                if text in table[0]:
                    names.append(table[0])
                if text == '!all':
                    names.append(table[0])
        return JsonResponse({"names": names}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
def stock_detail(request, name):
    return JsonResponse({"name": "<TODO: get stock detalils>"}, status=200)