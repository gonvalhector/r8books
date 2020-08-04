import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import books, reviews

# Create your views here.
def index(request):
    """Search for a book by title, author or ISBN number."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "You must be logged in.")
            return HttpResponseRedirect(reverse("login"))
        return render(request, "review/index.html")
    # When the user submits a form (POST)
    else:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        # Request the submitted search query
        searchquery = request.POST["searchfield"]
        # If there is no search query
        if not searchquery:
            # Return error message
            messages.add_message(request, messages.ERROR, "Please, input a title, author or the ISBN number of a book.")
            return HttpResponseRedirect(reverse("index"))
        # Query the database for books by title
        #resultsbytitle = db.execute("SELECT * FROM books WHERE title LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbytitle = books.objects.filter(title__icontains=searchquery)
        # Query the database for books by author
        #resultsbyauthor = db.execute("SELECT * FROM books WHERE author LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbyauthor = books.objects.filter(author__icontains=searchquery)
        # Query the database for books by ISBN
        #resultsbyisbn = db.execute("SELECT * FROM books WHERE isbn LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbyisbn = books.objects.filter(isbn__icontains=searchquery)
        messages.add_message(request, messages.INFO, f"resultsbytitle: {resultsbytitle}\nresultsbyauthor: {resultsbyauthor}\nresultsbyisbn: {resultsbyisbn}")
        return HttpResponseRedirect(reverse("index"))

def register(request):
    """Display user registration form and register a new user."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        if request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "You are logged in. Log out to create an account.")
        return render(request, "review/register.html")
    # When the user submits a form (POST)
    else:
        # If the user is currently logged in
        if request.user.is_authenticated:
            messages.add_message(request, messages.ERROR, "Please log out before registering a new account.")
            return HttpResponseRedirect(reverse("register"))
        # Validate username
        username = request.POST["username"]
        # If no username is provided in field
        if not username:
            messages.add_message(request, messages.ERROR, "Please provide a username.")
            return HttpResponseRedirect(reverse("register"))
        # If username is longer than 150 characters
        if len(username) > 150:
            messages.add_message(request, messages.ERROR, "Please provide a username with 150 characters or fewer.")
            return HttpResponseRedirect(reverse("register"))
        # Validate optional first name
        first_name = request.POST["first_name"]
        if first_name:
            if len(first_name) > 30:
                messages.add_message(request, messages.ERROR, "Please provide a first name with 30 characters or fewer.")
                return HttpResponseRedirect(reverse("register"))
        # Validate optional last name
        last_name = request.POST["last_name"]
        if last_name:
            if len(last_name) > 150:
                messages.add_message(request, messages.ERROR, "Please provide a last name with 150 characters or fewer.")
                return HttpResponseRedirect(reverse("register"))
        # Validate optional email
        email = request.POST["email"]
        # Validate Password
        password = request.POST["password1"]
        password_confirm = request.POST["password2"]
        if not password:
            messages.add_message(request, messages.ERROR, "Please provide a password.")
            return HttpResponseRedirect(reverse("register"))
        if not password_confirm:
            messages.add_message(request, messages.ERROR, "Please provide a password confirmation.")
            return HttpResponseRedirect(reverse("register"))
        if password != password_confirm:
            messages.add_message(request, messages.ERROR, "Please provide a password confirmation that matches the password.")
            return HttpResponseRedirect(reverse("register"))
        if len(password) < 8:
            messages.add_message(request, messages.ERROR, "Please provide a password longer than 8 characters.")
            return HttpResponseRedirect(reverse("register"))
        # Check if the user already exists in the database
        try:
            if User.objects.get(username=username) or User.objects.get(email=email):
                messages.add_message(request, messages.ERROR, "That username or email have already been registered.")
                return HttpResponseRedirect(reverse("register"))
        except User.DoesNotExist:
            # Register new user
            newuser = User.objects.create_user(username, email, password)
            if first_name:
                newuser.first_name = first_name
            if last_name:
                newuser.last_name = last_name
            newuser.save()
            # Log user in
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, "Logged in succesfully!")
                return HttpResponseRedirect(reverse("index"))


def login_view(request):
    """Display the login page and log user in."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        return render(request, "review/login.html")
    # When the user submits a form (POST)
    else:
        # If the user is currently logged in
        if request.user.is_authenticated:
            messages.add_message(request, messages.ERROR, "Please log out first.")
            return HttpResponseRedirect(reverse("login"))
        username = request.POST["username"]
        if not username:
            messages.add_message(request, messages.ERROR, "Please provide a username.")
            return HttpResponseRedirect(reverse("login"))
        password = request.POST["password"]
        if not password:
            messages.add_message(request, messages.ERROR, "Please provide a password.")
            return HttpResponseRedirect(reverse("login"))
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.add_message(request, messages.ERROR, "User could not be authenticated.")
            return HttpResponseRedirect(reverse("login"))
        else:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Logged in succesfully!")
            return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    """Log user out."""

    logout(request)
    messages.add_message(request, messages.SUCCESS, "Logged out succesfully.")
    return HttpResponseRedirect(reverse("login"))
