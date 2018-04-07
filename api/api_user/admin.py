from django.contrib import admin

# Register your models here.
from api.api_user.models import CustomerDetail, UserOTP, ProfileDetails


admin.site.register(CustomerDetail)
admin.site.register(UserOTP)
admin.site.register(ProfileDetails)
