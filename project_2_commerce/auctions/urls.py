from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories/<slug:slug>", views.category_view, name="category"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create_listing, name="create"),
    path("history", views.history, name="history")
]
