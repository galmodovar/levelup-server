from django.db import models
from levelupapi.models.game import Game
from levelupapi.models.gamer import Gamer
from django.db.models import Count


class Event(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=55)
    date = models.DateField()
    time = models.TimeField()
    organizer = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(Gamer, through="EventGamer", related_name="attending")
    

