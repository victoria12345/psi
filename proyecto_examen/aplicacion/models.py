from django.db import models

class Pelicula(models.Model):
    nombreP= models.CharField(max_length = 128)

    def __str__(self):
        return self.nombreP

class Productora(models.Model):
    nombreP= models.CharField(max_length = 128)

    def __str__(self):
        return self.nombreP

class Produce(models.Model):
    # como nos piden que la primary key se llame pid
    pid = models.IntegerField(default=0, unique = True)
    coste = models.IntegerField(default=0)

    pelicula = models.ForeignKey(Pelicula, on_delete = models.CASCADE)
    productora = models.ForeignKey(Productora, on_delete= models.CASCADE)