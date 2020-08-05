from django.contrib import admin
from .models import books, reviews

# Register your models here.
admin.site.register(books)
admin.site.register(reviews)
