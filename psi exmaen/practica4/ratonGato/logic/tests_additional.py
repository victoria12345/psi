import re
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import Client, TransactionTestCase
from django.urls import reverse

from datamodel.models import Game

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
        self.paramsUser1_createGame = {"username": TEST_USERNAME_1,
                                       "password": TEST_PASSWORD_1,
                                       "return_service": '/mouse_cat'
                                                         '/create_game/'}
        self.paramsUser1_joinGame = {"username": TEST_USERNAME_1,
                                     "password": TEST_PASSWORD_1,
                                     "return_service": '/mouse_cat'
                                                       '/join_game/'}
        self.paramsUser1_selectGame = {"username": TEST_USERNAME_1,
                                       "password": TEST_PASSWORD_1,
                                       "return_service": '/mouse_cat/'
                                                         'select_game/'}
        self.paramsUser1_showGame = {"username": TEST_USERNAME_1,
                                     "password": TEST_PASSWORD_1,
                                     "return_service": '/mouse_cat/'
                                                       'show_game/'}

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

    @classmethod
    def loginTestUser(cls, client, user):
        client.force_login(user)

    @classmethod
    def logoutTestUser(cls, client):
        client.logout()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")

    def validate_login_required(self, client, service):
        self.logoutTestUser(client)
        response = client.get(reverse(service), follow=True)
        self.assertEqual(response.status_code, 200)
        self.is_login(response)

    def validate_anonymous_required(self, client, service):
        self.loginTestUser(client, self.user1)
        response = client.get(reverse(service), follow=True)
        self.assertEqual(response.status_code, 403)
        self.is_anonymous_error(response)

    def validate_response(self, service, response):
        definition = SERVICE_DEF[service]
        self.assertRegex(self.decode(response.content), definition["title"])
        m = re.search(definition["pattern"], self.decode(response.content))
        self.assertTrue(m)
        return m

    def is_login(self, response):
        self.validate_response(LOGIN_SERVICE, response)

    def is_login_error(self, response):
        self.validate_response(LOGIN_ERROR, response)

    def is_anonymous_error(self, response):
        self.validate_response(ANONYMOUSE_ERROR, response)

    def is_landing_autenticated(self, response, user):
        m = self.validate_response(LANDING_PAGE, response)
        self.assertEqual(m.group("username"), user.username)

    def is_signup_error1(self, response):
        self.validate_response(SIGNUP_ERROR_PASSWORD, response)

    def is_signup_error2(self, response):
        self.validate_response(SIGNUP_ERROR_USER, response)

    def is_signup_error3(self, response):
        self.validate_response(SIGNUP_ERROR_AUTH_PASSWORD, response)

    def is_counter_session(self, response, value):
        m = self.validate_response(COUNTER_SESSION_VALUE, response)
        self.assertEqual(Decimal(m.group("session_counter")), value)

    def is_counter_global(self, response, value):
        m = self.validate_response(COUNTER_GLOBAL_VALUE, response)
        self.assertEqual(Decimal(m.group("global_counter")), value)

    def is_join_game_error(self, response):
        self.validate_response(JOIN_GAME_ERROR_NOGAME, response)

    def is_clean_db(self, response, n_games):
        m = self.validate_response(CLEAN_SERVICE, response)
        self.assertEqual(Decimal(m.group("n_games_delete")), n_games)

    def is_select_game(self, response):
        self.validate_response(SELECT_GAME_SERVICE, response)

    def is_select_game_nocat(self, response):
        self.validate_response(SELECT_GAME_ERROR_NOCAT, response)

    def is_select_game_nomouse(self, response):
        self.validate_response(SELECT_GAME_ERROR_NOMOUSE, response)

    def is_play_game(self, response, game):
        m = self.validate_response(SHOW_GAME_SERVICE, response)
        board = ([0] * (Game.MAX_CELL - Game.MIN_CELL + 1))
        board[game.cat1] = board[game.cat2] = 1
        board[game.cat3] = board[game.cat4] = 1
        board[game.mouse] = -1
        self.assertEquals(m.group("board"), str(board))

    def is_play_game_moving(self, response, game):
        m = self.validate_response(PLAY_GAME_MOVING, response)
        self.assertEqual(game.cat_turn, m.group("turn") == "cat")
        self.assertEqual(not game.cat_turn, m.group("turn") == "mouse")

    def is_play_game_waiting(self, response, game):
        m = self.validate_response(PLAY_GAME_WAITING, response)
        self.assertEqual(game.cat_turn, m.group("turn") == "cat")
        self.assertEqual(not game.cat_turn, m.group("turn") == "mouse")


class PageShownAfterLogin(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_create_game(self):
        # Nos aseguramos de que el usuario no esta logeado.
        self.logoutTestUser(self.client1)
        # Hacemos un post de login especificando en return_service la direccion
        # de la pagina create_game, para, una vez se haga el login, ver si nos
        # devuelve a la pagina de create_game.
        webpage_html = self.client1.post(reverse(LOGIN_SERVICE),
                                         self.paramsUser1_createGame,
                                         follow=True).content
        # En la pagina devuelta, buscamos la frase "succesfully created by
        # user", que solo aparece en la pagina de create_game, y si la
        # encontramos, sera porque estamos en la pagina correcta.
        self.assertTrue('succesfully created by user' in str(webpage_html))

    def test_join_game(self):
        # Hacemos login con el usuario 2 y creamos un juego.
        self.loginTestUser(self.client1, self.user2)
        self.client1.get(reverse(CREATE_GAME_SERVICE), follow=True)
        # Hacemos logout con el usuario 2
        self.logoutTestUser(self.client1)
        # De la misma manera que en el test anterior, hacemos login con el
        # usuario 1 especificando el return_service de join_game, y, como hay
        # un juego creado del que no somos el gato, nos permite unirnos. Para
        # comprobar que despues del login nos deja entrar en join_game y
        # efectivamente nos une al juego, buscamos la frase "succesfully joined
        # to game". Si la encontramos, ha devuelto join_game correctamente.
        webpage_html = self.client1.post(reverse(LOGIN_SERVICE),
                                         self.paramsUser1_joinGame,
                                         follow=True).content
        self.assertTrue('succesfully joined to game' in str(webpage_html))

    def test_select_game(self):
        # Hacemos login con el usuario 2 y creamos un juego.
        self.loginTestUser(self.client1, self.user2)
        self.client1.get(reverse(CREATE_GAME_SERVICE), follow=True)
        # Nos logeamos con otro usuario, el user1:
        session = {"client": self.client1, "user": self.user1}
        self.loginTestUser(session["client"], session["user"])
        # Nos unimos a un juego con user1.
        self.client1.post(reverse(JOIN_GAME_SERVICE),
                          self.paramsUser1_joinGame, follow=True).content
        # Hacemos logout
        self.logoutTestUser(self.client1)
        # Intentamos hacer login especificando return_service a select_game
        # a ver si una vez hecho nos manda a la pagina select_game.
        webpage_html = self.client1.post(reverse(LOGIN_SERVICE),
                                         self.paramsUser1_selectGame,
                                         follow=True).content
        self.assertTrue('Games as mouse' in str(webpage_html))

    def test_show_selected_game_and_play(self):
        # Segun nuestra implementacion, si no se ha hecho login, no hay ningun
        # juego seleccionado, con lo cual al intentar visualizar un juego,
        # pedira el login y luego mostrara el mensaje "Seleccione antes un
        # juego", por lo que no va a haber ninguna diferencia entre que el
        # juego este perfectamente creado, nos hayamos unido, y lo hayamos
        # seleccionado y luego hecho logout, que si no existe ningun juego. Por
        # ello este test se hace sin crear nada previamente y simplemente se
        # comprueba que nos devuelva a show_game mostrando el mensaje de error.
        self.logoutTestUser(self.client1)
        webpage_html = self.client1.post(reverse(LOGIN_SERVICE),
                                         self.paramsUser1_showGame,
                                         follow=True).content
        self.assertTrue('Play' in str(webpage_html))
