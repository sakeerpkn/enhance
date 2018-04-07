from django.db import models
from django.contrib.auth.models import User
from api.api_baggage.models import Location
# Create your models here.



class Shelf(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1046)
    zone_id = models.ForeignKey(Location, models.DO_NOTHING,blank=True, null=True)
    created_user_id = models.ForeignKey(User, models.DO_NOTHING,blank=True, null=True,related_name="shelf_created_user_id")
    modified_user_id = models.ForeignKey(User, models.DO_NOTHING,blank=True, null=True,related_name="shelf_modified_user_id")
    created_on = models.DateTimeField(auto_now_add = True, editable=False,blank=True, null=True)
    modified_on = models.DateTimeField(auto_now = True, editable=False,blank=True, null=True)
    status = models.IntegerField(default=1) #0-inactive, 1-active



class ZoneToZoneManagerMapping(models.Model):
    id = models.AutoField(primary_key=True)
    zone_id = models.ForeignKey(Location, models.DO_NOTHING,blank=True, null=True, related_name='managers')
    manager_id = models.ForeignKey(User, models.DO_NOTHING,blank=True, null=True)
    created_user_id = models.ForeignKey(User, models.DO_NOTHING,blank=True, null=True,related_name="zone_mapping_created_user_id")
    modified_user_id = models.ForeignKey(User, models.DO_NOTHING,blank=True, null=True,related_name="zone_mapping_modified_user_id")
    created_on = models.DateTimeField(auto_now_add = True, editable=False,blank=True, null=True)
    modified_on = models.DateTimeField(auto_now = True, editable=False,blank=True, null=True)
    status = models.IntegerField(default=1) #0-inactive, 1-active
    



