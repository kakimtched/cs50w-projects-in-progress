from django.utils.text import slugify

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category_name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    author = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    creation_date = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="won_listings")
    watchlist = models.ManyToManyField(User, blank=True, related_name="user_watchlist")
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.amount}"
