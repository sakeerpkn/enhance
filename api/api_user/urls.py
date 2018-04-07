from django.conf.urls import url

from api.api_user.views import CustomerCreate, HandlerDataViewSet


urlpatterns = [
    url(r'^customer/register/$', CustomerCreate.as_view()),
    #url(r'^customer/(?P<pk>[^/]+)/$', CustomerViewSet.as_view()),


    url(r'^detail/$', HandlerDataViewSet.as_view({'get':'list'})),

]