from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, 'review/index.html')

def register(request):
    return HttpResponse('TODO /register')

def login_view(request):
    return HttpResponse('TODO /login')

def logout_view(request):
    return HttpResponse('TODO /logout')
