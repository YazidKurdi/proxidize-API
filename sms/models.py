from django.db import models

from modems.models import Modem


class SMS(models.Model):

    modem = models.ForeignKey(Modem, on_delete=models.CASCADE, related_name='modem')
    date = models.DateTimeField()
    phone_number = models.CharField(max_length=15)
    content = models.TextField()
    timestamp = models.FloatField()
