from django.contrib import admin

# Register your models here.
from api.api_ern_burn.models import *

admin.site.register(EarnActionDetail)
admin.site.register(BurnActionDetail)
admin.site.register(EarnTransaction)
admin.site.register(BurnTransaction)
admin.site.register(EarnBurnTransaction)
admin.site.register(Summary)
admin.site.register(EarnBurnSettings)