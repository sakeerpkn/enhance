from rest_framework import serializers

from base_app.models import Country, City, State, Shop, BaseShopCategory, StatusLevel, PushMessage, Profession


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'country']


class BaseShopCategorySerializer(serializers.ModelSerializer):
    no_of_stores = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = BaseShopCategory
        fields = ['id', 'name', 'image','no_of_stores']


    def get_no_of_stores(self,obj):
        return Shop.objects.filter(category=obj).count()


    def get_image(self, obj):
        try: return obj.image.url
        except: return None


class StatusLevelSerializer(serializers.ModelSerializer):
    level = serializers.StringRelatedField()
    id = serializers.IntegerField(source='priority')
    badge = serializers.SerializerMethodField()

    class Meta:
        model = StatusLevel
        fields = ('id', 'level', 'slab_starts', 'slab_ends','badge')

    def get_badge(self,obj):
        if obj.level.badge:
            return obj.level.badge.url
        return ""


class PushSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = PushMessage
        fields = ['id', 'receiver', 'message_content', 'status','created_at']


    def get_created_at(self,obj):
        try:
            from pytz import timezone
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            loc_dt = obj.created_at.astimezone(timezone('Asia/Kolkata'))
            return loc_dt.strftime(fmt)
        except Exception as e:
            print(e)
            return obj.created_at


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id','name',]