from django.contrib import admin

from .models import Listing, Comment, Bid

# Register your models here.


# Spec 7:
# "Django Admin Interface: 
#  Via the Django admin interface, a site administrator should be able to
#  view, add, edit, and delete any listings, comments, and bids made on the site."

# Intentionally not registering my other models (User and Category)
# to strictly comply with Specification 7.

admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)
