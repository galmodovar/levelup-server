from django.db import models
from levelupapi.models.gamer import Gamer
from levelupapi.models.gametype import GameType


class Game(models.Model):
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    gamer= models.ForeignKey(Gamer, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    maker = models.CharField(max_length=55)
    num_of_players = models.IntegerField()
    skill_level = models.IntegerField()
