from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view

from base_app.filters import ShopFilter
from base_app.models import City, State, Country, Shop, StatusLevel, PushMessage, Profession
from base_app.serializers import CitySerializer, StateSerializer, CountrySerializer, \
    StatusLevelSerializer, PushSerializer, ProfessionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from customer.serializers import ShopLimitedSerilaizer


class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class StateList(generics.ListAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all()


class CityList(generics.ListAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.all()




class StatusLevelList(generics.ListAPIView):
    serializer_class = StatusLevelSerializer
    queryset = StatusLevel.objects.filter(status=1)


class PushMessageList(generics.ListAPIView):
    serializer_class = PushSerializer
    queryset = PushMessage.objects.filter(status=1).order_by('-created_at')

    def get_queryset(self):
        limit = self.request.query_params.get('limit', 9)
        offset = self.request.query_params.get('offset', 0)
        receiver = self.request.query_params.get('receiver', None)
        dev_id = self.request.query_params.get('dev_id', None)
        if receiver and dev_id and receiver != None and dev_id != None:
            return self.queryset.filter(receiver=receiver)[int(offset):int(limit)]
        elif receiver and receiver != None:
            return self.queryset.filter(receiver=receiver)[int(offset):int(limit)]
        else:
            return PushMessage.objects.filter(status=1)

@api_view(['GET'])
def profession_and_shop_list(request):
    profession = Profession.objects.all()
    profession = ProfessionSerializer(profession, many=True)
    shops = Shop.objects.all().order_by('name')
    shop = ShopLimitedSerilaizer(shops, many=True)
    return Response({'professions':profession.data,'shops':shop.data})