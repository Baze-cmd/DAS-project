from django.shortcuts import render
from django.db import connections


def search(text):
    with connections['external'].cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        names = []
        for table in tables:
            names.append(table[0])
        # TODO: implement search functionality for text in names
    return names


def home(request):
    if not request.method == "POST":
        return render(request, 'home.html')

    text = request.POST.get('search')
    names = search(text)
    return render(request, 'home.html', {'names': names})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')