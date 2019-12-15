from django.db import models
from django.contrib.auth.models import User
import math
from django.core.exceptions import ValidationError
from datetime import datetime

# Dice fons que esto es guarro. Es facil hacerlo con cadenas para que luego
# imprimir sea simplemente imprimir el valor.


class GameStatus():
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    MIN_CELL = 0
    MAX_CELL = 63
    winner = models.ForeignKey(User,
                                   related_name='winner',
                                   null=True,
                                   blank=True,
                                   on_delete=models.CASCADE)
    cat_user = models.ForeignKey(User,
                                 related_name='games_as_cat',
                                 blank=False,
                                 on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User,
                                   related_name='games_as_mouse',
                                   null=True,
                                   blank=True,
                                   on_delete=models.CASCADE)
    cat1 = models.IntegerField(blank=False, default=0)
    cat2 = models.IntegerField(blank=False, default=2)
    cat3 = models.IntegerField(blank=False, default=4)
    cat4 = models.IntegerField(blank=False, default=6)
    mouse = models.IntegerField(blank=False, default=59)
    cat_turn = models.BooleanField(default=True)
    status = models.IntegerField(blank=False, default=GameStatus.CREATED)
    move_being_reproduced_user1 = models.IntegerField(blank=False, default=0)
    move_being_reproduced_user2 = models.IntegerField(blank=False, default=0)
    valid_squares = [0, 2, 4, 6, 9, 11, 13, 15, 16, 18, 20, 22, 25, 27, 29,
                     31, 32, 34, 36, 38, 41, 43, 45, 47, 48, 50, 52, 54, 57,
                     59, 61, 63]

    def get_winner(self):
        return self.winner

    def get_cat_user(self):
        return self.cat_user

    def get_mouse_user(self):
        return self.mouse_user

    def get_cat1(self):
        return self.cat1

    def get_cat2(self):
        return self.cat2

    def get_cat3(self):
        return self.cat3

    def get_cat4(self):
        return self.cat4

    def get_mouse(self):
        return self.mouse

    def get_cat_turn(self):
        return self.cat_turn

    def get_status(self):
        return self.status

    def get_move_being_reproduced_user1(self):
        return self.move_being_reproduced_user1

    def get_move_being_reproduced_user2(self):
        return self.move_being_reproduced_user2

    def get_valid_squares(self):
        return self.valid_squares

    # def set_winner(self):
    #     return self.winner
    #
    # def set_cat_user(self):
    #     return self.cat_user
    #
    # def set_mouse_user(self, mouse_user):
    #     self.mouse_user = mouse_user

    def set_cat1(self, cat):
        self.cat1 = cat

    def set_cat2(self, cat):
        self.cat2 = cat

    def set_cat3(self, cat):
        self.cat3 = cat

    def set_cat4(self, cat):
        self.cat4 = cat

    def set_mouse(self, mouse):
        self.mouse = mouse
    #
    # def set_cat_turn(self):
    #     return self.cat_turn
    #
    # def set_status(self):
    #     return self.status

    def set_move_being_reproduced_user1(self, move_being_reproduced_user1):
        self.move_being_reproduced_user1 = move_being_reproduced_user1

    def set_move_being_reproduced_user2(self, move_being_reproduced_user2):
          self.move_being_reproduced_user2 = move_being_reproduced_user2

    def set_valid_squares(self):
        return self.valid_squares

    def check_if_square_is_available(self, square):
        if ((square == self.cat1) or (square == self.cat2)
            or (square == self.cat3) or
            (square == self.cat4) or
                (square == self.mouse) or not(square in self.valid_squares)):
            return False
        else:
            return True

    def check_if_game_is_finished(self):
        pos_y_mouse = math.floor(int(self.mouse) / 8)
        pos_y_cat_1 = math.floor(int(self.cat1) / 8)
        pos_y_cat_2 = math.floor(int(self.cat2) / 8)
        pos_y_cat_3 = math.floor(int(self.cat3) / 8)
        pos_y_cat_4 = math.floor(int(self.cat4) / 8)
        ori_y = math.floor(int(self.mouse) / 8)

        ori_x = (int(self.mouse) % 8)
        dest_x1 = ori_x - 1
        dest_y1 = ori_y - 1
        dest1 = (dest_x1) + (dest_y1)*8
        dest_x2 = ori_x - 1
        dest_y2 = ori_y + 1
        dest2 = (dest_x2) + (dest_y2)*8
        dest_x3 = ori_x + 1
        dest_y3 = ori_y - 1
        dest3 = (dest_x3) + (dest_y3)*8
        dest_x4 = ori_x + 1
        dest_y4 = ori_y + 1
        dest4 = (dest_x4) + (dest_y4)*8

        if ((pos_y_mouse <= pos_y_cat_1) and
            (pos_y_mouse <= pos_y_cat_2) and
            (pos_y_mouse <= pos_y_cat_3) and
                (pos_y_mouse <= pos_y_cat_4)):
            self.status = GameStatus.FINISHED
            self.winner = self.mouse_user
        elif ((self.check_if_square_is_available(dest1) == False) and
              (self.check_if_square_is_available(dest2) == False) and
              (self.check_if_square_is_available(dest3) == False) and
                (self.check_if_square_is_available(dest4) == False)):
              self.status = GameStatus.FINISHED
              self.winner = self.cat_user
              return;




    # cuenta el numero de filas en la tabla por ese juego
    @property
    def moves(self):
        return Move.objects.filter(game=self)

    def set_mouse_user(self, user):
        self.mouse_user = user
        self.save()
        return True

    # Check cats and mouse are situated in a valid square before saving:
    def save(self, *args, **kwargs):
        # Esto de gamestatus creo que no hace falta, creo que cuando se aniade
        # el segundo usuario tambien se cambia manualmente el status.
        if (self.status != GameStatus.FINISHED):
            self.check_if_game_is_finished()
        if ((self.mouse_user is not None) and
                (self.status == GameStatus.CREATED)):
            self.status = GameStatus.ACTIVE
        if ((self.cat1 in self.valid_squares) and
            (self.cat2 in self.valid_squares) and
            (self.cat3 in self.valid_squares) and
            (self.cat4 in self.valid_squares) and
                (self.mouse in self.valid_squares)):
            return super(Game, self).save(*args, **kwargs)
        else:
            raise ValidationError("Invalid cell for a cat or the mouse|Gato o\
                                  ratón en posición no válida")

    def clean_fields(self, *args, **kwargs):
        self.check_if_game_is_finished()
        if ((self.cat1 in self.valid_squares) and
            (self.cat2 in self.valid_squares) and
            (self.cat3 in self.valid_squares) and
            (self.cat4 in self.valid_squares) and
                (self.mouse in self.valid_squares)):
            return super(Game, self).clean_fields(*args, **kwargs)
        else:
            raise ValidationError("Invalid cell for a cat or the mouse|Gato o\
                                  ratón en posición no válida")

    def __str__(self):
        # ASUMIMOS QUE EL GATO NO PUEDE MOVER HASTA QUE NO SE UNA EL RATON.
        if (self.status == GameStatus.CREATED):
            status_aux = "Created"
        elif (self.status == GameStatus.ACTIVE):
            status_aux = "Active"
        else:
            status_aux = "Finished"

        if (self.mouse_user is None):
            return ("(" + str(self.id) + ", " + status_aux + ")\t" +
                    "Cat [X] cat_user_test(" + str(self.cat1) + ", "
                    + str(self.cat2) +
                    ", " + str(self.cat3) + ", " + str(self.cat4) + ")")
        else:
            if (self.cat_turn):
                return ("(" + str(self.id) + ", " + status_aux + ")\t" +
                        "Cat [X] cat_user_test(" + str(self.cat1) + ", " +
                        str(self.cat2) + ", " + str(self.cat3) + ", " +
                        str(self.cat4) + ") --- Mouse [ ] mouse_user_test(" +
                        str(self.mouse) + ")")
            else:
                return ("(" + str(self.id) + ", " + status_aux + ")\t" +
                        "Cat [ ] cat_user_test(" + str(self.cat1) + ", " +
                        str(self.cat2) + ", " + str(self.cat3) + ", " +
                        str(self.cat4) + ") --- Mouse [X] mouse_user_test(" +
                        str(self.mouse) + ")")


class Move(models.Model):
    origin = models.IntegerField(blank=False, null=False)
    target = models.IntegerField(blank=False, null=False)
    # moves = models.IntegerField(blank=False, null=False, default=0)
    game = models.ForeignKey(Game,
                             related_name='move_game_game',
                             on_delete=models.CASCADE)
    player = models.ForeignKey(User,
                               related_name='move_user_player',
                               on_delete=models.CASCADE)
    date = models.DateField(blank=False,
                            null=False,
                            default=datetime.now().strftime("%Y-%m-%d"))
    cat_movement = models.BooleanField(blank=True, null=True)
    cat_being_moved = models.IntegerField(blank=True, null=True, default=0)

    def get_origin(self):
        return self.origin

    def get_target(self):
        return self.target

    def get_game(self):
        return self.game

    def get_player(self):
        return self.player

    def get_date(self):
        return self.date

    def get_cat_movement(self):
        return cat_movement

    def get_cat_being_moved(self):
        return self.cat_being_moved

    def check_target_square_is_available(self):
        if ((self.target == self.game.cat1) or (self.target == self.game.cat2)
            or (self.target == self.game.cat3) or
            (self.target == self.game.cat4) or
                (self.target == self.game.mouse)):
            return False
        else:
            return True
    # devuelve false si se esta moviendo un
    def check_which_cat_is_being_moved(self):
        if (self.origin == self.game.cat1):
            self.cat_being_moved = 1
        elif (self.origin == self.game.cat2):
            self.cat_being_moved = 2
        elif (self.origin == self.game.cat3):
            self.cat_being_moved = 3
        elif (self.origin == self.game.cat4):
            self.cat_being_moved = 4
        else:
            self.cat_being_moved = -1
            return False
        return True

    def valid_movement(self):
        if (not self.game.status == GameStatus.ACTIVE):
            return False
        if (self.check_target_square_is_available() is False):
            return False
        # We turn the square nomenclature into tuples because this way it's
        # easier to find out if the movement is permitted or not.
        # La coordenada x es el numero de casilla entre 8 (division entera) + 1
        ori_x = math.floor(int(self.origin) / 8) + 1
        # La coordenada y es el numero de casilla modulo 8 + 1
        ori_y = (int(self.origin) % 8) + 1
        # Con el destino igual:
        dest_x = (math.floor(int(self.target) / 8)) + 1
        dest_y = (int(self.target) % 8) + 1

        # Check we are in a cat movement or not because cat is only allowed to
        # move south while mouse is allowed to move in any direction.
        if (self.player == self.game.cat_user):
            if (self.game.cat_turn is False):
                return False
            # it's a cat movement. Check which cat we are moving and that we
            # are actually moving a cat:
            self.cat_movement = True
            if (not self.check_which_cat_is_being_moved()):
                return False
            #  Given a square S, the adyacent squares that are underneath of it
            # are at a distant such that x in destination is 1 more position,
            # because we are moving one row down, and y is either 1 more
            # position or one less, because we can only move one column right
            # or one column left.
            if (((ori_x - dest_x) == -1) and
                (((ori_y - dest_y) == -1) or ((ori_y - dest_y) == 1)) and
                (0 < dest_x) and (9 > dest_x) and (0 < dest_y) and
                    (9 > dest_y)):
                return True
            else:
                return False
        else:
            # it's a mouse movement. Check if origin is the mouse position.
            self.cat_movement = False
            if (self.game.cat_turn is True):
                return False
            if (self.origin != self.game.mouse):
                return False
            # 4 possible combinations: one row up and one column right
            # (difference of (1, 1) in the tuples substraction), one row up and
            # one column left (difference of (1, -1) in the tuples
            # substraction)) and so on.
            if ((((ori_x - dest_x) == -1) or ((ori_x - dest_x) == 1)) and
                (((ori_y - dest_y) == -1) or ((ori_y - dest_y) == 1)) and
                (0 < dest_x) and (9 > dest_x) and (0 < dest_y) and
                    (9 > dest_y)):
                return True
            else:
                return False

    def update_squares_and_turn(self):
        if(self.cat_movement):
            if (self.cat_being_moved == 1):
                self.game.cat1 = self.target
            elif (self.cat_being_moved == 2):
                self.game.cat2 = self.target
            elif (self.cat_being_moved == 3):
                self.game.cat3 = self.target
            elif (self.cat_being_moved == 4):
                self.game.cat4 = self.target
            else:
                self.game.cat4 = self.target
            self.game.cat_turn = False
        else:
            self.game.mouse = self.target
            self.game.cat_turn = True

    def save(self, *args, **kwargs):

        if((self.player != self.game.cat_user) and
                (self.player != self.game.mouse_user)):
            raise ValidationError("Move not allowed|Movimiento no permitido")
            return False
        if (self.valid_movement()):
            self.update_squares_and_turn()
            self.game.save()
            return super(Move, self).save(*args, **kwargs)
        else:
            raise ValidationError("Move not allowed|Movimiento no permitido")
            return False


class CounterManager(models.Manager):

    # funcion para cuando no haya ningun counter en la base
    # de datos introducirlo
    def counter_ini(self):
        c = Counter()

        # hacemos que se guarde
        super(Counter, c).save()
        return c

    def get_current_value(self):
        counters = super().get_queryset()

        if len(counters) == 0:
            return 0
        return counters[0].value

    def inc(self):
        val = self.get_current_value()

        # si no hay ninguno todavia
        if val == 0:
            counter = self.counter_ini()
        else:
            counter = super().get_queryset()
            counter = counter[0]
        val = val + 1
        counter.value = val
        super(Counter, counter).save()

        return val


class Counter(models.Model):
    # valor del counter
    value = models.IntegerField(default=0)
    objects = CounterManager()

    # aqui sera donde lancemos la ValidationError
    # Hay que sobreescribir el save
    def save(self, *args, **kwargs):
        raise ValidationError("Insert not allowed|Inseción no permitida")
