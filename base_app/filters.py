from django_filters import rest_framework as filters

from base_app.models import Shop, BaseShopCategory


class ShopFilter(filters.FilterSet):
    category = filters.ModelMultipleChoiceFilter(queryset=BaseShopCategory.objects.all())
    name = filters.CharFilter(name="name", method='custom_name_filter')

    class Meta:
        model = Shop
        fields = ['category', 'name']

    def custom_name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class BaseShopCategoryFilter(filters.FilterSet):
    name = filters.CharFilter(name="name", method='custom_name_filter')

    class Meta:
        model = BaseShopCategory
        fields = ['name', ]

    def custom_name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
