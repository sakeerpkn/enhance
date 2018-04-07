from django_filters import rest_framework as filters

from api.api_ern_burn.models import EarnActionDetail, BurnActionDetail
from newsfeed.models import NewsFeed


class NewsFeedFilter(filters.FilterSet):
    category = filters.ChoiceFilter

    class Meta:
        model = NewsFeed
        fields = ['category']


class EarnActionFilter(filters.FilterSet):
    shop = filters.CharFilter(method='custom_shop_filter')

    class Meta:
        model = EarnActionDetail
        fields = ['shop']

    def custom_shop_filter(self, queryset, name, value):
        return queryset.filter(shop__name__icontains = value)


class BurnActionFilter(filters.FilterSet):
    shop = filters.CharFilter(method='custom_shop_filter')

    class Meta:
        model = BurnActionDetail
        fields = ['shop']

    def custom_shop_filter(self, queryset, name, value):
        return queryset.filter(shop__name__icontains = value)