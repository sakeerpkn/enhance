"""enhance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include, static
from rest_framework.routers import DefaultRouter

from api import api_user
from api.api_baggage.views import CustomerBagViewSet, CustomerToHanderStoreCreateSet, \
    CustomerInitiateDeliveryBagCreateSet, \
    HandlerToCustomerDeliveryBagCreateSet, \
    HandlerToHandlerAcceptBagCreateSet, \
    HandlerToZoneAcceptCreateSet, \
    ZoneToHandlerAcceptBagCreateSet, \
    CustomerToZoneStoreCreateSet, \
    ZoneToCustomerDeliveryBagCreateSet, \
    CustomerLocations, \
    HandlerPushNotification, \
    TamperBagViewSet, \
    GetTamperBagHistoryViewSet, PhysicalLocationList, WhereIsMyTamperBag, GetTamperBaHistoryViewSet

from api.api_user.views import ListZonersHandlersView, \
    UpdateZonersHandlersData, \
    UserLogin, HandlerDataViewSet, CreateZonerHandlerSet

from api.api_zone.views import ZoneBaggageViewSet, ZoneShelf, \
    ZonerToShelfTransferCreateSet, BaggageViewSet

from api.api_user import views as api_user_view
from base_app.views import CountryList, StateList, CityList, StatusLevelList, PushMessageList, profession_and_shop_list

from api.api_baggage.api_global_modules import device_register, send_message
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^baggages/get_count/$', CustomerBagsViewSet),
    url(r'^admin-management/', include('api.api_admin_management.urls')),
    url(r'^zone_managers/', api_user_view.ZoneManagerList.as_view()),
    url(r'^user-management/', include('api.api_user.urls')),
    url(r'^physical_location/$',PhysicalLocationList.as_view()),
    url(r'^country/$', CountryList.as_view()),
    url(r'^state/$', StateList.as_view()),
    url(r'^city/$', CityList.as_view()),
    url(r'^request-otp/$', api_user.views.request_for_otp, name='request_for_otp'),
    url(r'^verify-otp/$', api_user.views.otp_verification, name='verify_otp'),
    url(r'^customer-logout', api_user.views.customer_logout, name='customer_logout'),
    url(r'^earn-burn-management/', include('api.api_ern_burn.urls')),
    url(r'^where-is-my-tamper-bag/$', WhereIsMyTamperBag.as_view()),
    url(r'^news/', include('newsfeed.urls')),
    url(r'^status-level/$', StatusLevelList.as_view()),
    url(r'^push-messages/$', PushMessageList.as_view()),
    url(r'^bag-transactions/$', GetTamperBagHistoryViewSet.as_view()),
    url(r'^devices/register$', device_register),
    url(r'^devices/send_message$', send_message),
    url(r'', include('fcm.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^profession_and_shop/$', profession_and_shop_list),

]
router = DefaultRouter()
router.register(r'baggage', CustomerBagViewSet)
router.register(r'locations', CustomerLocations)

router.register(r'customer-handler-store-bag', CustomerToHanderStoreCreateSet)
router.register(r'customer-initiate-delivery-bag', CustomerInitiateDeliveryBagCreateSet)
router.register(r'handler-customer-delivery-bag', HandlerToCustomerDeliveryBagCreateSet)

# router.register(r'handler-handler-transfer-bag', HandlerToHandlerTransferBagCreateSet)
router.register(r'handler-handler-accept-bag', HandlerToHandlerAcceptBagCreateSet)

# router.register(r'handler-zone-transfer-bag', HandlerToZoneTransferCreateSet)
router.register(r'handler-zone-accept-bag', HandlerToZoneAcceptCreateSet)

# router.register(r'zone-handler-transfer-bag', ZoneToHandlerTransferBagCreateSet)
router.register(r'zone-handler-accept-bag', ZoneToHandlerAcceptBagCreateSet)

router.register(r'customer-zone-store-bag', CustomerToZoneStoreCreateSet)
router.register(r'zone-customer-delivery-bag', ZoneToCustomerDeliveryBagCreateSet)

router.register(r'handler-notification', HandlerPushNotification)

router.register(r'baggage-list', ZoneBaggageViewSet)
router.register(r'baggage-list2', BaggageViewSet)

router.register(r'zone-shelf', ZoneShelf)
router.register(r'zoner-shelf-transfer-bag', ZonerToShelfTransferCreateSet)
router.register(r'user-list', ListZonersHandlersView)
router.register(r'user-data-update', UpdateZonersHandlersData)
router.register(r'user-login', UserLogin)
router.register(r'verify-handler', HandlerDataViewSet)

router.register(r'create-zoner-handler', CreateZonerHandlerSet)

router.register(r'bag-information', TamperBagViewSet)
router.register(r'bag-history-information', GetTamperBaHistoryViewSet)

# router.register(r'handler-zone-store-bag', HandlerToZoneStoreBagCreateSet)

# router.register(r'zone-handler-delivery-bag', ZoneToHandlerDeliveryBagCreateSet)
# router.register(r'handler-handler-delivery-bag', HandlerToHandlerDeliveryBagCreateSet)


# router.register(r'get-user-otp', CreateUserOtpSet)
# router.register(r'verify-user-otp', VerifyUserOtpSet)
from enhance import settings

urlpatterns += router.urls
urlpatterns+=  static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


