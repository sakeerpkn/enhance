from django.db import models
from django.contrib.auth.models import User
from api.api_user.models import CustomerDetail
from django.db.models.fields import BLANK_CHOICE_DASH


# Create your models here.


class ImageGallery(models.Model):
    
    IMAGE_TYPES = ((0, "image"), (1, "Banner image"),  (2, "Newsfeed image"), (3, "Newsfeed Banner image"))
    
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=512, null=True, blank=True)    
    
    image_type = models.IntegerField(default=0, choices=IMAGE_TYPES)
    image = models.ImageField(upload_to='image_gallery', null=True, blank=True)
    tag = models.CharField(max_length=256, null=True, blank=True)
    
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        if self.title:
            return self.title
        return self.image.url   


class CustomerQueryType(models.Model):
    title = models.CharField(max_length=256,null=True,blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='category_created')
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='query_category_modified')
    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.title)

class CustomerQuery(models.Model):
    
    STATE_TYPES = ((0, 'Received'), (1, 'Approved'), (2, 'Rejected'), (2, 'Sent Response'))
    
    query = models.TextField()
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    state = models.IntegerField(default=0, choices=STATE_TYPES)
    
    customer = models.ForeignKey(CustomerDetail, null=True, blank=True)
    query_type = models.ForeignKey(CustomerQueryType, null=True, blank=True)
    
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='customer_query_type')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.query
    
    
class CustomerSocialMediaConnection(models.Model):
    
    CONNECT_TYPE = ((0, 'facebook'), (1, 'google'), (2, 'twitter'), (3, 'instagram'))
    
    connect_type = models.IntegerField(choices=CONNECT_TYPE, null=True, blank=True)
    user = models.ForeignKey(User, related_name='social_media_connection')
    unique_string = models.CharField(max_length=512, null=True, blank=True)
    
    
class CustomerInvite(models.Model):
    
    INVITE_TYPE = ((0, 'SMS'), (1, 'EMAIL'))
    INVITE_STATUS = (("PENDING", 'PENDING'), ('SENT', 'SENT'), ('FAILED', 'FAILED'))
    
    customer = models.ForeignKey(CustomerDetail)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=256, null=True, blank=True)
    invite_type = models.IntegerField(choices=INVITE_TYPE, default=0)
    invite_status = models.CharField(max_length=15, default='PENDING', choices=INVITE_STATUS)
    is_active = models.BooleanField(default=True)
    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user.user_id.username)