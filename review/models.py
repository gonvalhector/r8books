from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class books(models.Model):
    isbn = models.CharField(max_length=13)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=128)
    year = models.CharField(max_length=4)

class reviews(models.Model):
    book_id = models.ForeignKey(books, on_delete=models.CASCADE, related_name="submissions")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    rating = models.SmallIntegerField()
    reviewtext = models.TextField()
