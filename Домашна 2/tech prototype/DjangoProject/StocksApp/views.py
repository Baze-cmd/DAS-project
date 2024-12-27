from django.db import connections
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

original_sys_path = sys.path.copy()
sys.path = [path for path in sys.path if 'site-packages' not in path]
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../Домашна 3/src')))
sys.path.append(os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages'))
import analysis

sys.path = original_sys_path


def get_table_names(limit=None):
    connection = connections['external']
    cursor = connection.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    if limit is not None:
        query += f" LIMIT {limit}"
    try:
        cursor.execute(query)
        table_names = cursor.fetchall()
    finally:
        cursor.close()
    return [table[0] for table in table_names]


@csrf_exempt
def homepage(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only get method is allowed"}, status=405)
    front_page = get_table_names(8)
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
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    table_names = get_table_names()
    names = []
    for name in table_names:
        if text in name:
            names.append(name)
        if text == '!all':
            names.append(name)
    return JsonResponse({"names": names}, status=200)


def get_stock_data(name):
    connection = connections['external']
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT Date, Last_trade_price, Max, Min FROM {name}")
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    finally:
        cursor.close()
    df = pd.DataFrame(rows, columns=column_names)
    # reverse the order of the data
    df = df.iloc[::-1].reset_index(drop=True)
    return df




@csrf_exempt
def stock_data(request, name):
    df = get_stock_data(name)
    if request.method == 'GET':
        df.drop(columns=['Max', 'Min'], inplace=True)
        response_data = {'data': df.to_dict(orient='records')}
        return JsonResponse(response_data, status=200)

    if request.method == 'POST':
        try:
            time_period = json.loads(request.body).get('timePeriod')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        df = analysis.filter_data(df, time_period)
        indicators = analysis.calc_indicators(df)
        response_data = {'indicators': indicators}
        return JsonResponse(response_data, status=200)
