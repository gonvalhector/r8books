import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import books, reviews

# Create your views here.
def index(request):
    """Search for a book by title, author or ISBN number."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        if not request.user.is_authenticated:
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
            message = "Please, input a title, author or the ISBN number of a book."
            return render(request, "review/index.html", {"message": message})
        # Query the database for books by title
        #resultsbytitle = db.execute("SELECT * FROM books WHERE title LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbytitle = books.objects.filter(title__icontains=searchquery)
        print(resultsbytitle)
        # Query the database for books by author
        #resultsbyauthor = db.execute("SELECT * FROM books WHERE author LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbyauthor = books.objects.filter(author__icontains=searchquery)
        print(resultsbyauthor)
        # Query the database for books by ISBN
        #resultsbyisbn = db.execute("SELECT * FROM books WHERE isbn LIKE :searchquery", {"searchquery": searchquery}).fetchall()
        resultsbyisbn = books.objects.filter(isbn__icontains=searchquery)
        print(resultsbyisbn)
        message = f"resultsbytitle: {resultsbytitle}\nresultsbyauthor: {resultsbyauthor}\nresultsbyisbn: {resultsbyisbn}"
        return render(request, "review/index.html", {"message": message})

def register(request):
    """Display user registration form and register a new user."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        if request.user.is_authenticated:
            message = "You are logged in. Log out to create an account."
        else:
            message = None
        return render(request, "review/register.html", {"message": message})
    # When the user submits a form (POST)
    else:
        # If the user is currently logged in
        if request.user.is_authenticated:
            return render(request, "review/register.html", {"message": "Please log out before registering a new account."})
        # Validate username
        username = request.POST["username"]
        # If no username is provided in field
        if not username:
            return render(request, "review/register.html", {"message": "Please provide a username."})
        # If username is longer than 150 characters
        if len(username) > 150:
            return render(request, "review/register.html", {"message": "Please provide a username with 150 characters or fewer."})
        # Validate optional first name
        first_name = request.POST["first_name"]
        if first_name:
            if len(first_name) > 30:
                return render(request, "review/register.html", {"message": "Please provide a first name with 30 characters or fewer."})
        # Validate optional last name
        last_name = request.POST["last_name"]
        if last_name:
            if len(last_name) > 150:
                return render(request, "review/register.html", {"message": "Please provide a last name with 150 characters or fewer."})
        # Validate optional email
        email = request.POST["email"]
        # Validate Password
        password = request.POST["password1"]
        password_confirm = request.POST["password2"]
        if not password:
            return render(request, "review/register.html", {"message": "Please provide a password."})
        if not password_confirm:
            return render(request, "review/register.html", {"message": "Please provide a password confirmation."})
        if password != password_confirm:
            return render(request, "review/register.html", {"message": "Please provide a password confirmation that matches the password."})
        if len(password) < 8:
            return render(request, "review/register.html", {"message": "Please provide a password longer than 8 characters."})
        # Check if the user already exists in the database
        try:
            if User.objects.get(username=username) or User.objects.get(email=email):
                return render(request, "review/register.html", {"message": "That username or email have already been registered."})
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
            return render(request, "review/login.html", {"message": "Please log out first."})
        username = request.POST["username"]
        if not username:
            return render(request, "review/login.html", {"message": "Please provide a username."})
        password = request.POST["password"]
        if not password:
            return render(request, "review/login.html", {"message": "Please provide a password."})
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "review/login.html", {"message": "User does not exist."})
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    """Log user out."""

    logout(request)
    return HttpResponseRedirect(reverse("login"))

def add_to_db(request):
    # Open books file
    f = open("books.csv")
    # Read the csv file
    reader = csv.reader(f)
    # Skip the headers row
    next(reader, None)
    # Iterate over every row in the csv file
    for isbn, title, author, year in reader:
        #db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        b = books(isbn=isbn, title=title, author=author, year=year)
        b.save()
    return HttpResponseRedirect(reverse("index"))
