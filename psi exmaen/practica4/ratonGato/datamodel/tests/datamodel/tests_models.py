"""
@author: rlatorre
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import tests
from .models import Counter, Game, GameStatus, Move


class GameModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Crear juego válido con un único jugador """
        game = Game(cat_user=self.users[0])
        game.full_clean()
        game.save()
        self.assertIsNone(game.mouse_user)
        self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
        self.assertTrue(game.cat_turn)
        self.assertEqual(game.status, GameStatus.CREATED)

    
class MoveModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Movimientos válidos """
        game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1], status=GameStatus.ACTIVE)
        moves = [
            {"player": self.users[0], "origin": 0, "target": 9},
            {"player": self.users[1], "origin": 59, "target": 50},
            {"player": self.users[0], "origin": 2, "target": 11},
        ]

        n_moves = 0
        for move in moves:
            Move.objects.create(
                game=game, player=move["player"], origin=move["origin"], target=move["target"])
            n_moves += 1
            self.assertEqual(game.moves.count(), n_moves)

    def test2(self):
        """ Movimientos en un juego no activo """
        game = Game(cat_user=self.users[0])
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(game=game, player=self.users[0], origin=0, target=9)


class CounterModelTests(TestCase):
    def setUp(self):
        Counter.objects.all().delete()

    def test1(self):
        """ No es posible crear un nuevo contador """
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            Counter.objects.create()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            Counter.objects.create(value=0)

    def test2(self):
        """ No es posible crear un nuevo contador """
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter()
            n.save()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter(0)
            n.save()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter(11)
            n.save()

    def test3(self):
        """ Incremento a través del singleton """
        self.assertEqual(Counter.objects.inc(), 1)
        self.assertEqual(Counter.objects.inc(), 2)

    def test4(self):
        """ No es posible crear contadores """
        Counter.objects.inc()
        Counter.objects.inc()

        for i in [3, 4]:
            Counter.objects.inc()
            n = Counter.objects.get(value=i)
            self.assertEqual(n.value, i)
            with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
                n.save()

    def test5(self):
        """ Devolución correcta del valor del contador """
        self.assertEqual(Counter.objects.get_current_value(), 0)
        Counter.objects.inc()
        self.assertEqual(Counter.objects.get_current_value(), 1)
