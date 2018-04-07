from django.contrib import admin

# Register your models here.
from api.api_baggage.models import CustomerBag, Bag

admin.site.register(Bag)
admin.site.register(CustomerBag)
