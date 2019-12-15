import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')


django.setup()
from datamodel.models import Game, Move, GameStatus
from django.contrib.auth.models import User


if __name__ == '__main__':

    # Comprobar si existe un usuario con id=10 y si no existe crearlo. Recordar
    # que Django aniade automaticamente a todas las tablas del modelo un
    # atributo id que actua como clave primaria.objects.get_or_create(id=10)[0]

    u1 = User.objects.get_or_create(id=10, username="user10")[0]

    # Comprobar si existe un usuario con id=11 y si no existe crearlo.
    u2 = User.objects.get_or_create(id=11, username="user11")[0]

    # Crear un juego y asignarselo al usuario con id=10. Si os hiciera falta
    # en el futuro, tras persistir el objeto de tipo Game, su id se puede
    # obtener como nombre objeto game.id.
    g = Game.objects.get_or_create(cat_user=u1)[0]
    g.save()

    # Buscar todos los juegos con un solo usuario asignado. Imprimir el
    # resultado de la busqueda por pantalla.
    games = Game.objects.filter(status=GameStatus.CREATED)
    print("Juegos en estado created (con un solo usuario asignado): ")
    print(games)

    if (games.count() > 0):
        # Unir al usuario con id=11 al juego con menor id encontrado en el
        # paso anterior y comenzar la partida. Imprimir el objeto de tipo Game
        # encontrado por pantallaself.
        games[0].set_mouse_user(u2)
    # print("El mouse user de games[0] es: " + str(games[0].mouse_user))
    # games[0].full_clean()
    # print("El status de game es: " + str(games[0].status))
    games = Game.objects.filter(status=GameStatus.ACTIVE)
    print("Juego con el mouse_user aniadido: ")
    print(games[0])

    # En la partida seleccionada, mover el segundo gato pas´andolo de la
    # posicion 2 a la 11. Imprimir el objeto de tipo Game modificado por
    # pantalla.
    m = Move(origin=2, target=11, game=games[0], player=u1)
    m.save()
    # games = Game.objects.filter(status=GameStatus.ACTIVE)
    print("Game tras el movimiento del gato:")
    print(games[0])

    m = Move(origin=59, target=52, game=games[0], player=u2)
    # m.full_clean()
    m.save()
    # games = Game.objects.filter(status=GameStatus.ACTIVE)
    print("Game tras el movimiento del raton:")
    print(games[0])
