from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment


def index(request):
    user = request.user
    active = Listing.objects.filter(is_active=True)
    closed = []

    if user.is_authenticated:
        for listing in Listing.objects.filter(is_active=False):
            if listing.owner == user or listing.winner == user:
                closed.append(listing)

    return render(request, "auctions/index.html", {
        "listings": active,
        "closed": closed
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category_view(request, slug):
    category = Category.objects.get(slug=slug)
    category_listings = Listing.objects.filter(category=category, is_active=True)

    return render(request, "auctions/category.html", {
        "category": category,
        "listings": category_listings
    })


def listing_view(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    error_message = None
    user = request.user

    if request.method == "POST":

        if not user.is_authenticated:
            return redirect('login')

        action = request.POST.get("action")

        if action == "add_watchlist":
            listing.watchlist.add(user)
        elif action == "remove_watchlist":
            listing.watchlist.remove(user)     

        elif action == "place_bid":
            if listing.is_active:
                bid_amount = request.POST.get("bid")
                if bid_amount:
                    try:
                        bid_value = float(bid_amount)
                        if bid_value <= listing.price:
                            raise ValueError
                        Bid.objects.create(listing=listing, user=user, amount=bid_value)
                        listing.price = bid_value
                        listing.save()
                    except ValueError:
                        error_message = "Your bid must be higher than the current price."
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "error": error_message
                        })
        
        elif action == "close_auction":
            if user == listing.owner and listing.is_active:
                highest_bid = listing.bids.order_by("-amount").first()
                if highest_bid:
                    listing.winner = highest_bid.user
                else:
                    listing.winner = None
                listing.is_active = False
                listing.save()


        elif action == "add_comment":
            comment = request.POST.get("comment")
            if comment:
                Comment.objects.create(listing=listing, user=user, comment_text=comment)
        return redirect("listing", listing_id=listing_id)

    winner = listing.winner if listing.winner else None

    highest_bid = listing.bids.order_by("-amount").first()
    winning_bid = highest_bid.amount if highest_bid else None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "winner": winner,
        "winning_bid": winning_bid,
        "highest_bid": highest_bid,
        "error": error_message,
    })


@login_required
def history(request):
    user = request.user

    listings = Listing.objects.filter(
        Q(owner=user) | Q(winner=user),
        is_active = False
    )
    return render(request, "auctions/history.html", {
        "listings": listings
    })


@login_required
def watchlist(request):
    user = request.user
    listings = user.user_watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        author = request.POST.get("author")
        price = request.POST.get("price")
        image_url = request.POST.get("image_url")
        category_id = request.POST.get("category")
        owner = request.user
        
        if category_id:
            category_obj = Category.objects.get(id=category_id)
        else:
            category_obj = Category.objects.get(category_name="Other")

        Listing.objects.create(
            title=title,
            description=description,
            author=author,
            price=price,
            image_url=image_url,
            category=category_obj,
            owner=owner
        )
        return HttpResponseRedirect(reverse("index"))
   
    else:
        return render(request, "auctions/create_listing.html", {
            "categories": Category.objects.all()
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
