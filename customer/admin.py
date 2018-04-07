from django.contrib import admin

# Register your models here.
from customer.models import ImageGallery, CustomerQueryType, CustomerQuery, CustomerInvite

admin.site.register(ImageGallery)
admin.site.register(CustomerQueryType)
admin.site.register(CustomerQuery)
admin.site.register(CustomerInvite)
