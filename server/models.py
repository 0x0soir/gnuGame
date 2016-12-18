from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Game(models.Model):
    proprietaryUser = models.ForeignKey(User, null=False, related_name='game_proprietaryUsers')
    gplUser = models.ForeignKey(User, null=True, related_name='game_gplUsers')
    proprietary1 = models.IntegerField(default=0, null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    proprietary2 = models.IntegerField(default=2, null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    proprietary3 = models.IntegerField(default=4, null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    proprietary4 = models.IntegerField(default=6, null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    gpl = models.IntegerField(default=59, null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    proprietaryTurn = models.BooleanField(default=True, null=False)

    def __str__(self):
        if self.proprietaryUser == None:
            tmp_proprietaryUser = "-"
        else:
            tmp_proprietaryUser = self.proprietaryUser.username

        if self.gplUser == None:
            tmp_gplUser = "-"
        else:
            tmp_gplUser = self.gplUser.username
        return "ID: "+str(self.id)+" | Proprietary: "+tmp_proprietaryUser+" | Raton: "+tmp_gplUser

class Move(models.Model):
    origin = models.IntegerField(null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    target = models.IntegerField(null=False, validators=[MaxValueValidator(63), MinValueValidator(0)])
    game = models.ForeignKey(Game, null=False, related_name='move_games')

    def __str__(self):
        return str(self.origin)

class Counter(models.Model):
    value = models.IntegerField(default=0, null=False)

    def __str__(self):
        return str(self.value)
