"""
Couple djangorestframework and cities_light.

It defines a urlpatterns variables, with the following urls:

- cities-light-api-city-list
- cities-light-api-city-detail
- cities-light-api-region-list
- cities-light-api-region-detail
- cities-light-api-country-list
- cities-light-api-country-detail

If rest_framework (v3) is installed, all you have to do is add this url
include::

    path('cities_light/api/',
         include('cities_light.contrib.restframework3')),

And that's all !
"""
import django_filters
from django.urls import include, path
from django_filters import rest_framework as filters
from rest_framework import relations, routers, viewsets
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from ..loading import get_cities_models

Country, Region, SubRegion, City = get_cities_models()


class CityFilter(filters.FilterSet):
    class Meta:
        model = City
        fields = ["country", "region", "subregion"]


class RegionFilter(filters.FilterSet):
    class Meta:
        model = Region
        fields = ["country"]


class SubRegionFilter(filters.FilterSet):
    class Meta:
        model = SubRegion
        fields = ["country", "region"]


class CitySerializer(ModelSerializer):
    """
    ModelSerializer for City.
    """
    country = PrimaryKeyRelatedField(many=False, read_only=True)
    region = PrimaryKeyRelatedField(many=False, read_only=True)
    subregion = PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = City
        exclude = ('slug',)


class SubRegionSerializer(ModelSerializer):
    """
    ModelSerializer for SubRegion.
    """
    country = PrimaryKeyRelatedField(many=False, read_only=True)
    region = PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = SubRegion
        exclude = ('slug',)


class RegionSerializer(ModelSerializer):
    """
    ModelSerializer for Region.
    """
    country = PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Region
        exclude = ('slug',)


class CountrySerializer(ModelSerializer):
    """
    ModelSerializer for Country.
    """

    class Meta:
        model = Country
        fields = '__all__'


class CitiesLightListModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        """
        queryset = super().get_queryset()

        if self.request.GET.get('q', None):
            return queryset.filter(name_ascii__icontains=self.request.GET['q'])

        return queryset


class CountryModelViewSet(CitiesLightListModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class RegionModelViewSet(CitiesLightListModelViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = RegionFilter

class SubRegionModelViewSet(CitiesLightListModelViewSet):
    serializer_class = SubRegionSerializer
    queryset = SubRegion.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = SubRegionFilter

class CityModelViewSet(CitiesLightListModelViewSet):
    """
    ListRetrieveView for City.
    """
    serializer_class = CitySerializer
    queryset = City.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = CityFilter

    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against search_names.
        """
        queryset = self.queryset

        if self.request.GET.get('q', None):
            return queryset.filter(
                search_names__icontains=self.request.GET['q'])

        return queryset


router = routers.SimpleRouter()
router.register(r'cities', CityModelViewSet, basename='cities-light-api-city')
router.register(r'countries', CountryModelViewSet,
                basename='cities-light-api-country')
router.register(r'regions', RegionModelViewSet,
                basename='cities-light-api-region')
router.register(r'subregions', SubRegionModelViewSet,
                basename='cities-light-api-subregion')

urlpatterns = [
    path('', include(router.urls)),
]
