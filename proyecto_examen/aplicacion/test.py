from django.test import TestCase
from aplicacion.models import Pelicula, Productora, Produce
from django.urls import reverse

# Create your tests here.
class Test(TestCase):

    def setUp(self):
        super().setUp()

    def test_examen(self):
        # primero borramos todo
        
        Pelicula.objects.all().delete()
        Productora.objects.all().delete()
        Produce.objects.all().delete()

        # creamos la pelicula 1001
        p1 = Pelicula.objects.get_or_create(id=1001, nombreP="pelicula1")[0]

        # creamos las dos productoras (1001 y 1002)
        r1 = Productora.objects.get_or_create(id=1001, nombreP="productora1")[0]
        r2 = Productora.objects.get_or_create(id=1002, nombreP="productora2")[0]

        # creamos la produccion 1001       
        c1 = Produce.objects.get_or_create(pid=1001, pelicula=p1, productora=r2, coste=100)[0]

        response = self.client.get(reverse("productora"), follow=True)
        
        # dado que esa productora(la de id 1001) no ha participado en ninguna pelicula
        # comprobamos que el mensaje de error aparezca en la template
        
        self.assertIn(b'No hay peliculas en las que esa productora haya participado',
                      response.content)
       
