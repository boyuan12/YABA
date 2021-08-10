from random import random
from django.db import models
from helpers import random_str

# Create your models here.
class Goal(models.Model):
    user = models.ForeignKey('auth.User', related_name='goals', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    end_date = models.DateField()

class Budget(models.Model):
    user = models.ForeignKey('auth.User', related_name='budget', on_delete=models.CASCADE)
    amount = models.IntegerField()
    category = models.CharField(max_length=12)
