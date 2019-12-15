"""
@author: rlatorre
"""

import re, json
from decimal import Decimal

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from datamodel.tests import BaseModelTest
from django.contrib.auth.models import User
from django.db.models import Max, Q
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from . import forms
from . import tests_services

GET_MOVE_SERVICE = "get_move"

TEST_USERNAME_1 = "testUserMouseCatBaseTest_1"
TEST_PASSWORD_1 = "hskjdhfhw"
TEST_USERNAME_2 = "testUserMouseCatBaseTest_2"
TEST_PASSWORD_2 = "kj83jfbhg"

USER_SESSION_ID = "_auth_user_id"

LANDING_PAGE = "landing"
LANDING_TITLE = r"<h1>Service catalog</h1>|<h1>Servicios</h1>"

ANONYMOUSE_ERROR = "Anonymous required"
ERROR_TITLE = "<h1>Error</h1>"

LOGIN_SERVICE = "login"
LOGIN_ERROR = "login_error"
LOGIN_TITLE = "<h1>Login</h1>"

LOGOUT_SERVICE = "logout"

SIGNUP_SERVICE = "signup"
SIGNUP_ERROR_PASSWORD = "signup_error1"
SIGNUP_ERROR_USER = "signup_error2"
SIGNUP_ERROR_AUTH_PASSWORD = "signup_error3"
SIGNUP_TITLE = r"<h1>Signup user</h1>|<h1>Alta de usuarios</h1>"

COUNTER_SERVICE = "counter"
COUNTER_SESSION_VALUE = "session_counter"
COUNTER_GLOBAL_VALUE = "global_counter"
COUNTER_TITLE = r"<h1>Request counters</h1>|<h1>Contadores de peticiones</h1>"

CREATE_GAME_SERVICE = "create_game"

JOIN_GAME_SERVICE = "join_game"
JOIN_GAME_ERROR_NOGAME = "join_game_error"
JOIN_GAME_TITLE = r"<h1>Join game</h1>|<h1>Unirse a juego</h1>"

CLEAN_SERVICE = "clean_db"
CLEAN_TITLE = r"<h1>Clean orphan games</h1>|<h1>Borrar juegos huérfanos</h1>"

SELECT_GAME_SERVICE = "select_game"
SELECT_GAME_ERROR_NOCAT = "select_game_error1"
SELECT_GAME_ERROR_NOMOUSE = "select_game_error2"
SELECT_GAME_TITLE = r"<h1>Select game</h1>|<h1>Seleccionar juego</h1>"

SHOW_GAME_SERVICE = "show_game"
PLAY_GAME_MOVING = "play_moving"
PLAY_GAME_WAITING = "play_waiting"
SHOW_GAME_TITLE = r"<h1>Play</h1>|<h1>Jugar</h1>"

MOVE_SERVICE = "move"

SERVICE_DEF = {
    LANDING_PAGE: {
        "title": LANDING_TITLE,
        "pattern": r"<span class=\"username\">(?P<username>\w+)</span>"
    },
    ANONYMOUSE_ERROR: {
        "title": ERROR_TITLE,
        "pattern": r"Action restricted to anonymous \
                    users|Servicio restringido a usuarios anónimos"
    },
    LOGIN_SERVICE: {
        "title": LOGIN_TITLE,
        "pattern": r"Log in to continue:|Autenticarse para continuar:"
    },
    LOGIN_ERROR: {
        "title": LOGIN_TITLE,
        "pattern": r"Username/password is not valid|Usuario/clave no válidos"
    },
    SIGNUP_ERROR_PASSWORD: {
        "title": SIGNUP_TITLE,
        "pattern": r"Password and Repeat password are \
                    not the same|La clave y su repetición no coinciden"
    },
    SIGNUP_ERROR_USER: {
        "title": SIGNUP_TITLE,
        "pattern": r"A user with that username already \
                    exists|Usuario duplicado"
    },
    SIGNUP_ERROR_AUTH_PASSWORD: {
        "title": SIGNUP_TITLE,
        "pattern": r"(?=.*too short)(?=.*at least 6 char\
                    acters)(?=.*too common)"
    },
    COUNTER_SESSION_VALUE: {
        "title": COUNTER_TITLE,
        "pattern": r"Counter session: <b>(?P<session_counter>\d+)</b>"
    },
    COUNTER_GLOBAL_VALUE: {
        "title": COUNTER_TITLE,
        "pattern": r"Counter global: <b>(?P<global_counter>\d+)</b>"
    },
    JOIN_GAME_ERROR_NOGAME: {
        "title": JOIN_GAME_TITLE,
        "pattern": r"There is no available games|No hay juegos disponibles"
    },
    CLEAN_SERVICE: {
        "title": CLEAN_TITLE,
        "pattern": r"<b>(?P<n_games_delete>\d+)</b> (games removed \
                    from db|juegos borrados de la bd)"
    },
    SELECT_GAME_SERVICE: {
        "title": SELECT_GAME_TITLE,
        "pattern": r""
    },
    SELECT_GAME_ERROR_NOCAT: {
        "title": SELECT_GAME_TITLE,
        "pattern": r"No games as cat|No hay juegos disponibles como gato"
    },
    SELECT_GAME_ERROR_NOMOUSE: {
        "title": SELECT_GAME_TITLE,
        "pattern": r"No games as mouse|No hay juegos disponibles como ratón"
    },
    SHOW_GAME_SERVICE: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"(Board|Tablero): (?P<board>\[.*?\])"
    },
    PLAY_GAME_MOVING: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"<blockquote class=\"(?P<turn>\w+)\">(.|\n)*?"
                   r"<input type=\"submit\" value\
                    =\"Move\" />(.|\n)*?</blockquote>"
    },
    PLAY_GAME_WAITING: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"(Waiting for the|Esperando al) (?P<turn>\w+).{3}"
    },
}


class ServiceBaseTest(TransactionTestCase):
    def setUp(self):
        self.paramsUser1 = {"username": TEST_USERNAME_1,
                                     "password": TEST_PASSWORD_1}
        self.paramsUser2 = {"username": TEST_USERNAME_2,
                            "password": TEST_PASSWORD_2}

        User.objects.filter(
            Q(username=self.paramsUser1_createGame["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

        self.user1 = User.objects.create_user(
            username=self.paramsUser1_createGame["username"],
            password=self.paramsUser1_createGame["password"])
        self.user2 = User.objects.create_user(
            username=self.paramsUser2["username"],
            password=self.paramsUser2["password"])

        self.client1 = self.client
        self.client2 = Client()

    def tearDown(self):
        User.objects.filter(
            Q(username=self.paramsUser1_createGame["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

class GetMoveServiceTests(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.game = Game.objects.create(
            cat_user=self.user1, mouse_user=self.user2, status=GameStatus.ACTIVE)
        self.moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 2, "target": 11},
        ]

        for move in self.moves:
            Move.objects.create(
                game=self.game, player=move["player"], origin=move["origin"], target=move["target"])
        self.game.status = GameStatus.FINISHED
        self.game.save()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ GET no permitido """
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        response = self.client.get(reverse(GET_MOVE_SERVICE), {"shift": 1}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test2(self):
        """ Secuencia de movimientos válidos """
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        n_move = 0
        for move in self.moves:
            response = self.client1.post(
                reverse(GET_MOVE_SERVICE), {"shift": 1}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            data = json.loads(self.decode(response.content))
            self.assertEqual(data["origin"], move["origin"])
            self.assertEqual(data["target"], move["target"])
            self.assertTrue(data["previous"])
            self.assertEqual(data["next"], n_move != len(self.moves)-1)
            n_move += 1

        self.moves.reverse()
        n_move = 0
        for move in self.moves:
            response = self.client1.post(
                reverse(GET_MOVE_SERVICE), {"shift": -1}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            data = json.loads(self.decode(response.content))
            self.assertEqual(data["origin"], move["target"])
            self.assertEqual(data["target"], move["origin"])
            self.assertTrue(data["next"])
            self.assertEqual(data["previous"], n_move != len(self.moves)-1)
            n_move += 1

class GameEndTests(tests_services.PlayGameBaseServiceTests):
    def test1(self):
        # Comprueba que el estado del juego se cambia automaticamente al
        # guardarse el juego con una situacion de partida terminada.
        game = Game.objects.create(cat_user=self.user1,
                                   mouse_user=self.user2,
                                   status=GameStatus.ACTIVE)
        game.set_mouse(2)
        game.set_cat1(32)
        game.set_cat2(34)
        game.set_cat3(36)
        game.set_cat4(38)
        game.save()

        self.assertEqual(game.status, GameStatus.FINISHED);

    def test2(self):
        # Comprueba que en una partida en la que hay una situacion de victoria
        # para uno de los jugadores, escribe correctamente cual de los
        # dos ha ganado.
        game = Game.objects.create(cat_user=self.user1,
                                   mouse_user=self.user2,
                                   status=GameStatus.ACTIVE)
        game.set_mouse(2)
        game.set_cat1(32)
        game.set_cat2(34)
        game.set_cat3(36)
        game.set_cat4(38)
        game.save()
        self.assertEqual(self.user2, game.get_winner());
