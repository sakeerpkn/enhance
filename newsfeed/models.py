from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from base_app.models import NhanceBaseModel
from customer.models import ImageGallery

DISCOUNT = 'Discount'
EVENT = 'Event'


class NewsFeed(NhanceBaseModel):
    CHOICES = (
        (DISCOUNT, 'Discount'),
        (EVENT, 'Event')
    )
    name = models.TextField()
    description = models.TextField()
    image = models.BinaryField(null=True, blank=True)
    images = models.ManyToManyField(ImageGallery, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=1)
    number_of_likes = models.PositiveIntegerField(default=0)
    number_of_attending = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='news_created')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='news_modified')
    category = models.CharField(choices=CHOICES, max_length=20,null=True,blank=True)

    def __str__(self):
        return self.name


class NewsFeedUserLike(NhanceBaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='liked_news')
    news_feed = models.ForeignKey(NewsFeed)
    status = models.NullBooleanField()  # while dislike update to 0
    attending = models.NullBooleanField()

    def __str__(self):
        return str(self.user)
