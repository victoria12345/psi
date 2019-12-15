from ratonGato import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import render, redirect
from logic.forms import UserForm, SignupForm, MoveForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datamodel.models import Counter, Game, GameStatus, Move
from django.http import JsonResponse
from datamodel import constants


def landing(request):
    if 'counter' not in request.session:
        request.session['counter'] = 0
    context_dict = {'user': request.user}
    return render(request, 'mouse_cat/index.html', context_dict)


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            counter_aux(request)
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def login_required(f):
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            counter_aux(request)

            cadena = '/mouse_cat/'+settings.LOGIN_URL
            cadena += '?next='
            cadena += request.path

            return redirect(cadena)
        else:
            return f(request, *args, **kwargs)
    return wrapped


@anonymous_required
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        valuenext = request.POST.get('return_service')
        form = UserForm(data=request.POST)
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                request.session['counter'] = 0
                if valuenext == 'None' or valuenext is None:
                    return render(request, 'mouse_cat/index.html')
                return redirect(valuenext)
            else:
                context_dict = {'user_form': UserForm(), 'is_authenticated': request.user.is_authenticated}
                return render(request, 'mouse_cat/login.html', context_dict)
        else:
            form.add_error('username',
                           "Username/password is not valid")
            context_dict = {'user_form': form, 'is_authenticated': request.user.is_authenticated}
            return render(request, 'mouse_cat/login.html', context_dict)
    else:
        valuenext = request.GET.get('next')
        context_dict = {'user_form': UserForm(), 'return_service': valuenext, 'is_authenticated': request.user.is_authenticated}
        return render(request, 'mouse_cat/login.html', context_dict)


def user_logout(request):
    if request.user.is_authenticated:
        request.session.pop('counter', None)
        context_dict = {'user': request.user.username}
        logout(request)
        return render(request, 'mouse_cat/logout.html', context_dict)
    else:
        return render(request, 'mouse_cat/index.html')


@anonymous_required
def signup(request):

    if request.method == 'POST':
        signup_form = SignupForm(data=request.POST)

        # si esto lo pasa con cleaned_data podemos acceder a los atributos
        if signup_form.is_valid():
            datos = signup_form.cleaned_data

            # comprobamos que las contrasennas sean iguales
            if(datos['password'] != datos['password2']):
                form = SignupForm(data=request.POST)
                form.add_error('username', "Password and Repeat\
                    password are not the same\
                    |La clave y su repetición no coinciden")
                user_form = {'user_form': form}
                return render(request, 'mouse_cat/signup.html', user_form)

            # si son iguales vemos que sean validas
            try:
                validate_password(datos['password'])
            except ValidationError as error:
                form = SignupForm(data=request.POST)
                error = str(error).split(',')
                form.add_error('username', error[:3])
                user_form = {'user_form': form}
                return render(request, 'mouse_cat/signup.html', user_form)

            # Pasado todo creamos el usuario e iniciamos sesion
            user = signup_form.save()

            # hacemos hash a la contrasenna y volvemos a guardar
            user.set_password(user.password)
            user.save()
            # autenticamos al usuario
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            request.session['counter'] = 0
            return render(request, 'mouse_cat/index.html')

        else:

            form = SignupForm(data=request.POST)
            user_form = {'user_form': form}
            return render(request, 'mouse_cat/signup.html', user_form)
            # error de no valido xd
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        # Render the template depending on the context.
        user_form = {'user_form': SignupForm()}
        return render(request, 'mouse_cat/signup.html', user_form)


def counter_aux(request):
    Counter.objects.inc()

    if 'counter' not in request.session:
        request.session['counter'] = 0

    request.session['counter'] += 1

def counter(request):

    if 'counter' not in request.session:
        request.session['counter'] = 0

    counter_session = request.session['counter']
    counter_global = Counter.objects.get_current_value()
    context_dict = {'counter_session': counter_session,
                    'counter_global': counter_global}
    return render(request, 'mouse_cat/counter.html', context_dict)


@login_required
def create_game(request):

    game = Game.objects.create(cat_user=request.user)
    context_dict = {'game': game}
    return render(request, 'mouse_cat/new_game.html', context_dict)


@login_required
def join_game(request):
    games = Game.objects.filter(status=GameStatus.CREATED)
    games = games.exclude(cat_user=request.user)
    games = games.order_by('-id')
    if (len(games) > 0):
        games[0].set_mouse_user(request.user)
        games[0].save()
        context_dict = {'game': games[0]}
    else:
        msg_error = "There is no available games|No hay juegos disponibles"
        context_dict = {'msg_error': msg_error}

    return render(request, 'mouse_cat/join_game.html', context_dict)


@login_required
def select_game(request, method, game_id=None):
    context_dict = {}
    if (game_id):
        game = Game.objects.filter(id=game_id)
        if (game.count() == 0):
            counter_aux(request)
            return HttpResponse('No existe ningun juego con ese id.',
                                status=404)
        game = game[0]
        request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
        if method == 'join_game':
            game.mouse_user = request.user
            game.save()

        if (game.status == GameStatus.ACTIVE):
            return redirect(reverse('show_game'))
        elif (game.status == GameStatus.FINISHED):
            return redirect(reverse('replay_game'))
        else:
            return HttpResponse('Debes seleccionar un juego con estado activo o finalizado.',
                                status=200)
    else:
        if method == 'join_game':
            games = Game.objects.filter(status=GameStatus.CREATED)
            games = games.exclude(cat_user=request.user)
            context_dict = {'games': list(games), 'method': method}

        elif method == 'play_game':
            as_cat = Game.objects.filter(cat_user=request.user)
            as_cat = as_cat.exclude(status=GameStatus.FINISHED)
            as_cat = as_cat.exclude(status=GameStatus.CREATED)
            as_cat = list(as_cat)

            as_mouse = Game.objects.filter(mouse_user=request.user)
            as_mouse = as_mouse.exclude(status=GameStatus.FINISHED)
            as_mouse = as_mouse.exclude(status=GameStatus.CREATED)
            as_mouse = list(as_mouse)

            context_dict = {'games': as_cat + as_mouse, 'method': method}

        elif method == 'replay_game':
            as_cat = Game.objects.filter(cat_user=request.user)
            as_cat = as_cat.exclude(status=GameStatus.ACTIVE)
            as_cat = as_cat.exclude(status=GameStatus.CREATED)
            as_cat = list(as_cat)

            as_mouse = Game.objects.filter(mouse_user=request.user)
            as_mouse = as_mouse.exclude(status=GameStatus.ACTIVE)
            as_mouse = as_mouse.exclude(status=GameStatus.CREATED)
            as_mouse = list(as_mouse)

            context_dict = {'games': as_cat + as_mouse, 'method': method}
        else:
            return errorHTTP(request, 'Método no implementado')

        return render(request, 'mouse_cat/select_game.html', context_dict)


@login_required
def move(request):
    if request.method == 'POST':
        game_id = request.session.get(constants.GAME_SELECTED_SESSION_ID)
        if not game_id:
            counter_aux(request)
            return HttpResponse("No existe el juego", status=404)
        game = Game.objects.filter(id=game_id)

        user = request.user

        # parametros que recibimos del post
        origin = int(request.POST['origin'])
        target = int(request.POST['target'])

        print(request.POST, request.user, game[0].cat_user, game[0].mouse_user)
        try:
            Move.objects.create(origin=origin,
                                target=target, game=game[0], player=user)
        except:
            pass

        return redirect(reverse('show_game'))
    else:
        counter_aux(request)
        return HttpResponse("Metodo no permitido", status=404)


@login_required
def show_game(request):
    if (constants.GAME_SELECTED_SESSION_ID in request.session):
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
        game = Game.objects.filter(id=game_id)

        # if (game[0].status == GameStatus.FINISHED):
        #     return render(request, 'mouse_cat/replay_game.html')

        board = [0]*64

        move = MoveForm()

        # miramos la casilla del raton y gatos
        board[game[0].mouse] = -1
        board[game[0].cat1] = 1
        board[game[0].cat2] = 1
        board[game[0].cat3] = 1
        board[game[0].cat4] = 1

        context_dict = {'game': game[0], 'board': board, 'move_form': move}

        return render(request, 'mouse_cat/game.html', context_dict)
    else:

        return render(request, 'mouse_cat/game.html')

def replay_game(request):
    terminado = 0
    if (constants.GAME_SELECTED_SESSION_ID in request.session):
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
        game = Game.objects.filter(id=game_id)[0]
        if (game.get_status() == GameStatus.FINISHED):
            mouse = 59
            cat1 = 0
            cat2 = 2
            cat3 = 4
            cat4 = 6

            board = [0]*64

            # miramos la casilla del raton y gatos
            board[mouse] = -1
            board[cat1] = 1
            board[cat2] = 1
            board[cat3] = 1
            board[cat4] = 1

            context_dict = {'game': game, 'board': board, 'terminado': terminado}
            if (request.user == game.get_cat_user()):
                game.set_move_being_reproduced_user1(0)
            else:
                game.set_move_being_reproduced_user2(0)
            game.save()
            return render(request, 'mouse_cat/replay_game.html', context_dict)
        else:
            counter_aux(request)
            return HttpResponse("El juego seleccionado no ha finalizado.", status=404)
    else:

        return render(request, 'mouse_cat/replay_game.html')

def get_move(request):
    if request.method == 'GET':
        counter_aux(request)
        return HttpResponse('get_move() debe llamarse con un post, no con un get.',
                            status=404)

    else:
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID];
        game = Game.objects.filter(id=game_id)
        if (len(game)>0):
            game = game[0]
        else:
            counter_aux(request)
            return HttpResponse('No se ha encontrado el juego.',
                                status=404)
        moves = game.moves
        shift = int(request.POST.get('shift'))
        if (request.user == game.get_cat_user()):
            move_counter = game.get_move_being_reproduced_user1();
        else:
            move_counter = game.get_move_being_reproduced_user2();
        if (shift < 0):
            move_counter += shift
        if (move_counter <= len(moves)):
            new_move = moves[move_counter]
            if shift > 0:
                response = {'origin': new_move.get_origin(),
                            'target': new_move.get_target(),
                            'previous': True,
                            'next': (len(moves) > int(move_counter) + 1)
                            }
            else:
                response = {'origin': new_move.get_target(),
                            'target': new_move.get_origin(),
                            'previous': (move_counter > 0),
                            'next': True
                            }
            if (shift > 0):
                move_counter += shift

            if (request.user == game.get_cat_user()):
                game.set_move_being_reproduced_user1(move_counter)
            else:
                game.set_move_being_reproduced_user2(move_counter)
            game.save()

            return JsonResponse(response, status=200)

        else:
            counter_aux(request)
            return HttpResponse('No quedan movimientos.',
                                status=404)


def is_it_my_turn(request):
    if request.method == 'GET':
        counter_aux(request)
        return HttpResponse('is_it_my_turn() debe llamarse con un post, no con un get.',
                            status=404)

    else:
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID];
        game = Game.objects.filter(id=game_id)
        if (len(game)>0):
            game = game[0]
        else:
            counter_aux(request)
            return HttpResponse('No se ha encontrado el juego.',
                                status=404)
        turn = ((request.user == game.cat_user and game.get_cat_turn())
                 or
                (request.user == game.mouse_user and not game.get_cat_turn()))
        response = {'is_it_my_turn': turn}
        return JsonResponse(response, status=200)

def get_game_status(request):
    game_id = request.session[constants.GAME_SELECTED_SESSION_ID];
    game = Game.objects.filter(id=game_id)
    if (len(game)>0):
        game = game[0]
    else:
        counter_aux(request)
        return HttpResponse('No se ha encontrado el juego.',
                            status=404)
    status = game.status
    winner = game.winner
    return JsonResponse({'status': status, 'winner': str(winner)}, status=200)

def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)
