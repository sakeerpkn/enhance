from __future__ import unicode_literals
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import random
import string


def create_qrcode():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class PhysicalLocation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    category = models.IntegerField()  # 1-zone, 2-parking 3- home etc
    created_user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                        related_name="zone_created_user_id")
    modified_user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                         related_name="zone_modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active
    physical_location = models.ForeignKey(PhysicalLocation, models.DO_NOTHING, blank=True, null=True,
                                          related_name="zones")
    capacity_limit = models.PositiveIntegerField(null=True, blank=True)
    total_shelves = models.PositiveIntegerField(null=True, blank=True)
    alias = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Bag(models.Model):
    id = models.AutoField(primary_key=True)
    # category = models.IntegerField()  # 1-handler bag, 2-Zone area
    qr_code = models.CharField(unique=True, max_length=254)
    name = models.CharField(max_length=1046)
    created_user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                        related_name="tamper_created_user_id")
    modified_user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                         related_name="tamper_modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active

    def __str__(self):
        return self.qr_code

    def save(self, *args, **kwargs):
        self.qr_code = create_qrcode()
        super(Bag, self).save(*args, **kwargs)


class CustomerBag(models.Model):
    id = models.AutoField(primary_key=True)
    cutomer_type = models.IntegerField(blank=True, null=True)  # 1-non nhance user(value=1), 2-enhance user(value=2)
    customer_id = models.CharField(max_length=512, blank=True,
                                   null=True)  # customer mobilenumber/qr code ( qr code for nhance user)
    customer_name = models.CharField(max_length=512, blank=True, null=True)
    location1 = models.CharField(max_length=512, blank=True, null=True)
    pick_up_time = models.DateTimeField(blank=True, null=True)  # current time
    transaction = models.CharField(max_length=512)
    parent_id = models.ForeignKey('CustomerBag', models.DO_NOTHING, blank=True, null=True)
    number_of_bags = models.IntegerField(blank=True, null=True)
    stored_location_id = models.CharField(max_length=512, blank=True, null=True)  # tamper bag qr code
    location2 = models.CharField(max_length=512, blank=True, null=True)
    shelf = models.CharField(max_length=512, blank=True, null=True)  # zone storage area
    drop_time = models.DateTimeField(blank=True, null=True)  # when it hand over to customer
    status = models.IntegerField(default=0)  # 0-incomplete, 1-complete
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    zone = models.ForeignKey('Location', models.DO_NOTHING, blank=True, null=True)
    customer_requested = models.IntegerField(blank=True, null=True)
    customer_requested_time = models.DateTimeField(blank=True, null=True) 
    customer_requested_place = models.ForeignKey('Location', models.DO_NOTHING, blank=True, null=True,related_name="customer_drop_request_place")

    # def __str__(self):
    #     if self.customer_name:
    #         return self.customer_name + ' - ' + self.customer_id
    #     return self.customer_id

