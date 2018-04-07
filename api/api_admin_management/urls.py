from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from api.api_admin_management.views import HandlerBagViewSet, ZoneListCreateViewSet, BaggageActionSet, \
    ZoneUpdateViewSet, tamper_bag_bulk_creation, BarCodePdfView

router = DefaultRouter()
router.register(r'handler-baggage', HandlerBagViewSet)
router.register(r'baggage', BaggageActionSet)
urlpatterns = [
    url(r'^zone/$', ZoneListCreateViewSet.as_view()),
    url(r'^zone/(?P<pk>[^/]+)/edit/$', ZoneUpdateViewSet.as_view()),
    url(r'^tamper-bag-create/$', tamper_bag_bulk_creation),
    url(r'^tamper-bag-pdf/$', BarCodePdfView),
]
urlpatterns += router.urls
