from django.db import models
from levelupapi.models.event import Event
from levelupapi.models.gamer import Gamer



class EventGamer(models.Model):
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)