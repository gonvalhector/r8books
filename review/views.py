import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import books, reviews
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import FieldError, FieldDoesNotExist, ObjectDoesNotExist
from django.db.models import Avg

# Create your views here.
def index(request):
    """Displays splash page."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        return render(request, "review/index.html")


def search(request):
    """Searches for a book by title, author or ISBN."""

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
            messages.add_message(request, messages.ERROR, "Please, input a title, author or ISBN of a book.")
            return HttpResponseRedirect(reverse("search"))
        return HttpResponseRedirect(reverse("results", args=(searchquery,)))


def empty_search(request):
    """Redirects to search view when the user forgets the query."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        # When the user is logged out
        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "You must be logged in.")
            return HttpResponseRedirect(reverse("login"))
        # Return error message and redirect user
        messages.add_message(request, messages.ERROR, "Please, input a title, author or ISBN of a book.")
        return HttpResponseRedirect(reverse("search"))


@csrf_protect
def search_results(request, searchquery):
    """Displays results of a search query."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        # If there is no search query
        if not searchquery:
            # Return error message
            messages.add_message(request, messages.ERROR, "Please, input a title, author or ISBN of a book.")
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
        year = book_data.year
        # Retrieve all reviews of book
        review_data = reviews.objects.filter(book_id=book_id)
        # Get ranges from reviews
        rev_data = []
        max = 5
        for review in review_data:
            username = review.user_id.username
            u = User.objects.get(username=username)
            if u.first_name and u.last_name:
                name = u.first_name + " " + u.last_name
            else:
                name = None
            rating = range(review.rating)
            remainder = range(max - review.rating)
            reviewtext = review.reviewtext
            rev_data.append({"rating": rating, "remainder": remainder, "username": username, "name": name, "reviewtext": reviewtext})
        context = {
            "title": title,
            "author": author,
            "isbn": isbn,
            "year": year,
            "rev_data": rev_data,
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

    # When the user is redirected or they follow a link
    if request.method == "GET":
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Logged out succesfully.")
        return HttpResponseRedirect(reverse("login"))


def api_view(request, isbn):
    """Returns information about a book from the database."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        # If the user is not authenticated
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR, "You must be an authenticated user to use R8Books's API.")
            return HttpResponseRedirect(reverse("login"))
        # Check book in database with ISBN number provided
        try:
            book_data = books.objects.get(isbn=isbn)
        except:
            # Return error response
            return JsonResponse({"error": "Book not found"}, status=404)
        # Define variables with data for response
        year = int(book_data.year)
        review_data = reviews.objects.filter(book_id=book_data)
        review_count = review_data.count()
        averaged = review_data.aggregate(Avg("rating"))
        average_score = averaged["rating__avg"]
        # Return response with book data
        return JsonResponse({
                "title": book_data.title,
                "author": book_data.author,
                "year": year,
                "isbn": isbn,
                "review_count": review_count,
                "average_score": average_score
            })


def import_view(request):
    """Imports data about 5000 books from a CSV file."""

    # When the user is redirected or they follow a link
    if request.method == "GET":
        # If the user belongs to the staff or is the admin
        if request.user.is_staff == True:
            # Open books file
            f = open("books.csv")
            # Read the csv file
            reader = csv.reader(f)
            # Skip the headers row
            next(reader, None)
            # Declare list of objects
            obj_list = []
            # Iterate over every row in the csv file
            for isbn, title, author, year in reader:
                # Create book object
                b = books(isbn=isbn, title=title, author=author, year=year)
                # Append book object to list
                obj_list.append(b)
            # Create db insertion of book objects in bulk
            books.objects.bulk_create(obj_list)
            # Redirect authorized user with success message
            messages.add_message(request, messages.SUCCESS, "Books imported succesfully!")
            return HttpResponseRedirect(reverse("index"))
        # If the user is unauthorized
        else:
            # Redirect unauthorized user with error message
            messages.add_message(request, messages.ERROR, "You don't have the required permissions.")
            return HttpResponseRedirect(reverse("index"))
