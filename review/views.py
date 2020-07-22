from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'review/index.html')

def register(request):
    '''Display user registration form and register a new user.'''
    # When the user is redirected or they follow a link
    if request.method == 'GET':
        if request.user.is_authenticated:
            message = 'You are logged in. Log out to create an account.'
        else:
            message = None
        return render(request, 'review/register.html', message)
    # When the user submits a form (POST)
    else:
        # If the user is currently logged in
        if request.user.is_authenticated:
            return render(request, 'review/register.html', {'message': 'Please log out before registering a new account.'})


def login_view(request):
    '''Display the login page and log user in.'''
    # When the user is redirected or they follow a link
    if request.method == 'GET':
        return render(request, 'review/login.html')

def logout_view(request):
    '''Log user out.'''
    # When the user is redirected or they follow a link
    if request.method == 'GET':
        return HttpResponse('TODO /logout')
