from django.urls import path

from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path("register", views.register, name="register"),
  path("login", views.login_view, name="login"),
  path("logout", views.logout_view, name="logout"),
  path("search", views.search, name="search"),
  path("search/", views.empty_search, name="empty_search"),
  path("search/<str:searchquery>", views.search_results, name="results"),
  path("book/<int:book_id>", views.book_page, name="book"),
  path("api/<str:isbn>", views.api_view, name="api"),
  path("import", views.import_view, name="import")
]
