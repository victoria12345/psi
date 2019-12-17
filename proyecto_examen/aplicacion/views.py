from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import render, redirect


from aplicacion.models import Productora, Pelicula, Produce
# Create your views here.

def productora(request):

    # obtenemos la productora indicada
    pr = list(Productora.objects.filter(id=1001))[0]

    # obtenemos la lista de producciones en las que ha trabajado
    produce_list = list(Produce.objects.filter(productora=pr))

    if len(produce_list) <= 0:
        context_dict = {'error': "No hay peliculas en las que esa productora haya participado", 'productora': pr}
        return render(request, 'productora.html', context_dict)

    L = []

    # annadimos a una lista las peliculas en las que ha trabajado la productora
    for produce in produce_list:
        L.append(produce.pelicula)

    context_dict = {'productora': pr, 'peliculas': L}
    
    return render(request, 'productora.html', context_dict)
