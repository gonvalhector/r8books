from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

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
        # Validate username
        username = request.POST['username']
        # If no username is provided in field
        if not username:
            return render(request, 'review/register.html', {'message': 'Please provide a username.'})
        # If username is longer than 150 characters
        if len(username) > 150:
            return render(request, 'review/register.html', {'message': 'Please provide a username with 150 characters or fewer.'})
        # Validate optional first name
        first_name = request.POST['first_name']
        if first_name:
            if len(first_name) > 30:
                return render(request, 'review/register.html', {'message': 'Please provide a first name with 30 characters or fewer.'})
        # Validate optional last name
        last_name = request.POST['last_name']
        if last_name:
            if len(last_name) > 150:
                return render(request, 'review/register.html', {'message': 'Please provide a last name with 150 characters or fewer.'})
        # Validate optional email
        email = request.POST['email']
        # Validate Password
        password = request.POST['password1']
        password_confirm = request.POST['password2']
        if not password:
            return render(request, 'review/register.html', {'message': 'Please provide a password.'})
        if not password_confirm:
            return render(request, 'review/register.html', {'message': 'Please provide a password confirmation.'})
        if password != password_confirm:
            return render(request, 'review/register.html', {'message': 'Please provide a password confirmation that matches the password.'})
        # Check if the user already exists in the database
        try:
            if User.objects.get(username=username) or User.objects.get(email=email):
                return render(request, 'review/register.html', {'message': 'That username or email have already been registered.'})
        except User.DoesNotExist:
            # Register new user
            newuser = User.objects.create_user(username, password)
            if first_name:
                newuser.first_name = first_name
            if last_name:
                newuser.last_name = last_name
            if email:
                newuser.email = email
            newuser.save()
            # Redirect user to login page
            return render(request, 'review/login.html', {'message': 'User created succesfully!'})

def login_view(request):
    '''Display the login page and log user in.'''
    # When the user is redirected or they follow a link
    if request.method == 'GET':
        return render(request, 'review/login.html')
    # When the user submits a form (POST)
    else:
        # If the user is currently logged in
        if request.user.is_authenticated:
            return render(request, 'review/login.html', {'message': 'Please log out before trying to log in again.'})

def logout_view(request):
    '''Log user out.'''
    # When the user is redirected or they follow a link
    if request.method == 'GET':
        return HttpResponse('TODO /logout')
