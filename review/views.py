import requests
import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import books, reviews
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import FieldError, FieldDoesNotExist, ObjectDoesNotExist
from django.conf import settings

# Create your views here.
def import_books(request):
    """Import 5000 books from a csv file"""
    # Open books file
    f = open("books.csv")
    # Read the csv file
    reader = csv.reader(f)
    # Skip the headers row
    next(reader, None)
    obj_list = []
    # Iterate over every row in the csv file
    for isbn, title, author, year in reader:
        b = books(isbn=isbn, title=title, author=author, year=year)
        obj_list.append(b)
    books.objects.bulk_create(obj_list)
    messages.add_message(request, messages.SUCCESS, f"Books succesfully imported!")
    return HttpResponseRedirect(reverse("search"))


def index(request):
    """Displays splash page"""

    return render(request, "review/index.html")


def search(request):
    """Searches for a book by title, author or ISBN number."""

    # When the user is logged out
    if not request.user.is_authenticated:
        messages.add_message(request, messages.WARNING, "You must be logged in.")
        return HttpResponseRedirect(reverse("login"))
    # When the user is redirected or they follow a link
    if request.method == "GET":
        return render(request, "review/search.html")
    # When the user submits a form (POST)
    else:
        # Request the submitted search query
        searchquery = request.POST["searchfield"]
        # If there is no search query
        if not searchquery:
            # Return error message
            messages.add_message(request, messages.ERROR, "Please, input a title, author or the ISBN number of a book.")
            return HttpResponseRedirect(reverse("search"))
        return HttpResponseRedirect(reverse("results", args=(searchquery,)))


def empty_search(request):
    """Redirects to search page when the user forgets the query."""

    # When the user is logged out
    if not request.user.is_authenticated:
        messages.add_message(request, messages.WARNING, "You must be logged in.")
        return HttpResponseRedirect(reverse("login"))
    # Return error message and redirect user
    messages.add_message(request, messages.ERROR, "Please, input a title, author or the ISBN number of a book.")
    return HttpResponseRedirect(reverse("search"))


@csrf_protect
def search_results(request, searchquery):
    """Displays results of a search query."""

    # If there is no search query
    if not searchquery:
        # Return error message
        messages.add_message(request, messages.ERROR, "Please, input a title, author or the ISBN number of a book.")
        return HttpResponseRedirect(reverse("search"))
    # When the user is logged out
    if not request.user.is_authenticated:
        messages.add_message(request, messages.WARNING, "You must be logged in.")
        return HttpResponseRedirect(reverse("login"))
    # Query the database for books by title
    resultsbytitle = books.objects.filter(title__icontains=searchquery)
    # Query the database for books by author
    resultsbyauthor = books.objects.filter(author__icontains=searchquery)
    # Query the database for books by ISBN
    resultsbyisbn = books.objects.filter(isbn__icontains=searchquery)
    context = {
        "searchquery": searchquery,
        "resultsbytitle": resultsbytitle,
        "resultsbyauthor": resultsbyauthor,
        "resultsbyisbn": resultsbyisbn,
    }
    return render(request, "review/results.html", context)


@csrf_protect
def book_page(request, book_id):
    """Displays a page with title, author, ISBN, publication year and reviews of a book."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        # Retrieve book object from db
        try:
            book_data = books.objects.get(id=book_id)
        # Return error message and redirect user
        except:
            messages.add_message(request, messages.ERROR, "Book was not found.")
            return HttpResponseRedirect(reverse("search"))
        title = book_data.title
        author = book_data.author
        isbn = book_data.isbn
        # Retrieve all reviews of book
        review_data = reviews.objects.filter(book_id=book_id)
        # Request book information from Goodreads API
        response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": settings.API_KEY, "isbns": isbn})
        goodreads = response.json()
        work_ratings_count = goodreads["books"][0]["work_ratings_count"]
        average_rating = goodreads["books"][0]["average_rating"]
        context = {
            "title": title,
            "author": author,
            "isbn": isbn,
            "review_data": review_data,
            "work_ratings_count": work_ratings_count,
            "average_rating": average_rating,
            "book_id": book_id
        }
        return render(request, "review/bookpage.html", context)
    # When the user submits a form (POST)
    else:
        # Check if the user has previously submitted a review
        review_check = reviews.objects.filter(book_id=book_id, user_id=request.user.id)
        # If the user has a previously submitted review
        if review_check:
            messages.add_message(request, messages.ERROR, "You cannot submit a review for this book again.")
            return HttpResponseRedirect(reverse("book", args=(book_id,)))
        # Request submitted review data
        rating = request.POST["rating"]
        reviewtext = request.POST["reviewtext"]
        # If there is no input in the reviewtext field
        if not reviewtext:
            # Return error
            messages.add_message(request, messages.ERROR, "Please, provide a review in the text field in order to submit a review.")
            return HttpResponseRedirect(reverse("book", args=(book_id,)))
        # Retrieve book object from db
        try:
            book_data = books.objects.get(id=book_id)
        # Return error message and redirect user
        except:
            messages.add_message(request, messages.ERROR, "Book was not found.")
            return HttpResponseRedirect(reverse("search"))
        # Insert review into database
        r = reviews(book_id=book_data, user_id=request.user, rating=rating, reviewtext=reviewtext)
        r.save()
        # Redirect to book page with success message
        messages.add_message(request, messages.SUCCESS, "Review submitted succesfully!")
        return HttpResponseRedirect(reverse("book", args=(book_id,)))

def register(request):
    """Displays user registration form and registers a new user."""

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
                return HttpResponseRedirect(reverse("search"))


def login_view(request):
    """Displays the login page and logs users in."""

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
            return HttpResponseRedirect(reverse("search"))


def logout_view(request):
    """Logs users out."""

    logout(request)
    messages.add_message(request, messages.SUCCESS, "Logged out succesfully.")
    return HttpResponseRedirect(reverse("login"))
