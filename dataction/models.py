import datetime

from django.db import models
from django.utils import timezone

''' modèle
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
'''

class pointGPS(models.Model):
    coord = models.CharField(max_length=100)
    lat = models.CharField(max_length=50)
    long = models.CharField(max_length=50)
    #éventullement mettre un char à la place de date
    shot_date = models.DateTimeField('photo date')
    clean_state = models.BooleanField(default=False)
    # pourcentage de certitude

    def __str__(self):
        return self.coord


        
