# R8Books

**[R8Books](https://r8book.herokuapp.com/)** is a [Django](https://www.djangoproject.com/) web application that lets registered users look books up by their title, author or ISBN number, then rate and write reviews for them.

# views.py

Declares every possible view that **[R8Books](https://r8book.herokuapp.com/)** uses(like register, login, search, etc.).

## Views

### index

Displays splash page.

### search

Searches for a book by title, author or ISBN.

### empty_search

Redirects to search view when the user forgets the query.

### search_results

Displays results of a search query.

### book_page

Displays a page with title, author, ISBN, publication year and reviews of a book.

### register

Displays user registration form and registers a new user.

### login_view

Displays the login page and logs users in.

### logout_view

Logs users out.

### api_view

Returns information about a book from the database.

### import_view

Imports data about 5000 books from a CSV file.

# Templates

## layout.html

Template file that contains the header elements, navigation bar and overall structure that will be used by every other HTML file with the help of the [Django](https://www.djangoproject.com/) [template language](https://docs.djangoproject.com/en/3.1/ref/templates/language/).

## index.HTML

Extends "layout.html" and displays a splash page with information about the usage, API and credits of **[R8Books](https://r8book.herokuapp.com/)**.

## register.html

Extends "layout.html" and displays a form that the user can fill with their desired Username, Password and a Password Confirmation.
It sends the submitted data to the "register" view via POST method.

## login.html

Extends "layout.html" and displays a form that lets users log in to the app with a Username and Password if their account information is in the database.
It sends the submitted data to the "login" view via POST method.

## search.html

Extends "layout.html" and displays a form that lets users look books up with the title, author or ISBN number of a book. Accepts partial queries.
It sends the submitted data to the "search_results" view via POST method.

## results.html

Extends "layout.html" and displays a list with every match found for every type of category (title, author and ISBN number). Every list item is a link that redirects the user to the "book_page" view of the selected book, book_id being the id number that belongs to that book in the database.

## bookpage.html

Extends "layout.html" and displays the book information of the selected book along with the average rating and rating count provided by the [Goodreads](https://www.goodreads.com/) API. It also displays user submitted reviews for the book and a form in which the user can submit a rating and a review of their own if they haven't done so already.
It sends the submitted data to the "book_page" view via POST method.

# Static Files

## style.scss

Customizes bootstrap classes and elements used within the HTML files with the Sass language.

## style.css

Compiled version of the style.scss file.

# Other Files

## books.csv

Spreadsheet that contains information about 5000 books.

# Credits and Resources

- **CSS Library:** [Bootstrap 4](https://getbootstrap.com/)
- **Color Scheme:** [Coolors](https://coolors.co/)
- **Icons:** [Iconmonstr](https://iconmonstr.com/)
- **Filter Generation:** [CSS Filter Generator](https://codepen.io/sosuke/pen/Pjoqqp)

Made by: **[Hector Raul Gonzalez Valdes](https://gonvalhector.github.io/)**
