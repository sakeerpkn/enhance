from django.contrib.auth.models import User
from django.db import models
from reportlab.lib.colors import black


# Create your models here.


class NhanceBaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.name)


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="states")

    def __str__(self):
        return str(self.name)


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name="cities")

    def __str__(self):
        return str(self.name)


class BaseAddress(NhanceBaseModel):
    addressline1 = models.CharField("Addressline 1", max_length=255, null=True, blank=True)
    addressline2 = models.CharField("Addressline 2", max_length=255, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=6,null=True, blank=True)

    country = models.ForeignKey('Country', on_delete=models.DO_NOTHING, null=True, blank=True)

    state = models.ForeignKey('State', on_delete=models.DO_NOTHING, null=True, blank=True)

    city = models.ForeignKey('City', on_delete=models.DO_NOTHING, null=True, blank=True)


class Profession(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.name)


class Shop(NhanceBaseModel):
    name = models.CharField(max_length=200)
    floor_number = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    status = models.BooleanField(default=1)
    shop_number = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='shop_created')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='shop_modified')
    category = models.ManyToManyField('BaseShopCategory')
    description = models.TextField(null=True)
    logo = models.ImageField(upload_to='shop_images', null=True, blank=True)


    def __str__(self):
        return self.name


class ShopStatus(NhanceBaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.DO_NOTHING)
    status_card_level = models.ForeignKey('StatusLevel', on_delete=models.DO_NOTHING, null=True, blank=True)
    multiplied_by = models.PositiveIntegerField()
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='shop_status_created')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='shop_status_modified')

    def __str__(self):
        return str(self.shop)


class BaseShopCategory(NhanceBaseModel):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shop_category', null= True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='shop_category_created')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='shop_category_modified')

    status = models.BooleanField(default=1)

    def __str__(self):
        return self.name


class MembershipLevel(NhanceBaseModel):
    name = models.CharField(max_length=100)
    badge = models.ImageField(upload_to='badge', null= True, blank=True)

    def __str__(self):
        return self.name


class StatusLevel(models.Model):
    priority = models.PositiveIntegerField(unique=True)
    slab_starts = models.FloatField(default=0.00)
    slab_ends = models.FloatField(default=0.00)
    created_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name="created_user_id")
    modified_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name="modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active

    level = models.OneToOneField(MembershipLevel, models.DO_NOTHING)

    def __str__(self):
        return str(self.level) + '-' + str(self.slab_starts)



class PushMessage(NhanceBaseModel):
    receiver = models.CharField(max_length=20)
    dev_id = models.CharField(max_length=255, blank=True, null=True)
    message_content = models.CharField( max_length=255)
    status = models.BooleanField(default=1) # 0-not send, 1-send


class NhanceDocuments(models.Model):
    
    DETAIL_TYPE =  ((0, "About Us"),)

    detail_type = models.IntegerField(default=0, choices=DETAIL_TYPE)
        
    title = models.CharField(max_length=512, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now_add=True)

