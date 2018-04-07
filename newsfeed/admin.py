from django.contrib import admin

# Register your models here.
from newsfeed.models import NewsFeed, NewsFeedUserLike

admin.site.register(NewsFeed)
admin.site.register(NewsFeedUserLike)
