import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'proyecto.settings')


django.setup()
from aplicacion.models import Pelicula, Productora, Produce
from django.contrib.auth.models import User

if __name__ == '__main__':

    # comprobamos si existe pelicula con esos id's y si no las creamos
    p1 = Pelicula.objects.get_or_create(id=1001, nombreP="pelicula_a")[0]
    p2 = Pelicula.objects.get_or_create(id=1002, nombreP="pelicula_b")[0]
    p3 = Pelicula.objects.get_or_create(id=1003, nombreP="pelicula_c")[0]

    # comprobamos si existen productoras con esos id's y si no las creamos
    r1 = Productora.objects.get_or_create(id=1001, nombreP="productora_a")[0]
    r2 = Productora.objects.get_or_create(id=1002, nombreP="productora_b")[0]
    r3 = Productora.objects.get_or_create(id=1003, nombreP="productora_c")[0]
    r4 = Productora.objects.get_or_create(id=1004, nombreP="productora_d")[0]

    # comprobamos si existen produces con esos id's y si no las creamos
    c1 = Produce.objects.get_or_create(pid=1001, pelicula=p1, productora=r1, coste=100)[0]
    c2 = Produce.objects.get_or_create(pid=1002, pelicula=p2, productora=r2, coste=200)[0]
    c3 = Produce.objects.get_or_create(pid=1003, pelicula=p2, productora=r3, coste=100)[0]
    c4 = Produce.objects.get_or_create(pid=1004, pelicula=p1, productora=r3, coste=150)[0]
    

