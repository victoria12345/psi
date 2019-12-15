from django.http import HttpResponse


def index(request):
    return HttpResponse("Esta es la view index de mi aplicacion datamodel")
