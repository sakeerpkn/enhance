from django.contrib import admin

# Register your models here.
from base_app.models import Country, State, City, Shop, BaseShopCategory, ShopStatus, MembershipLevel, StatusLevel,\
    NhanceDocuments

admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Shop)
admin.site.register(BaseShopCategory)
admin.site.register(ShopStatus)
admin.site.register(MembershipLevel)
admin.site.register(StatusLevel)
admin.site.register(NhanceDocuments)