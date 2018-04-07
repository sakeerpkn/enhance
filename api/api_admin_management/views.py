from api.api_baggage.filter import ZoneFilter
from api.api_baggage.models import Bag, Location
from django.contrib.auth.models import User
from api.api_baggage.serializers import BaggageDetailsSerializer, LocationSerializer, BaggageListSerializer, \
    LocSerializer
from api.api_baggage.views import ListRetrieveViewSet, CreateViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework import mixins, generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse

from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

from enhance.settings import PDF_ROOT, ZIP_ROOT
import shutil
from django.http import HttpResponse
from wsgiref.util import FileWrapper


class CreateUpdateDeleteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
                                mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    pass


def tamper_bag_bulk_creation(request):
    """
    Description: This is used to create tamper proof bags 500 at a time
    Author : Sakeer P
    Created At: 26th Feb 2018

    """
    try:

        created_user = User.objects.get(id=1)
        insert_pmc_list = []
        insert_pal_list = []
        pmc_list = ['PMC' + str('{:03d}').format(x) for x in range(1, 351)]
        pal_list = ['PAL' + str('{:03d}').format(x) for x in range(1, 151)]
        number = 0
        for pmc in pmc_list:
            number = int(number) + 1
            qr = str('{:04d}').format(number)
            insert_pmc_list.append(
                Bag(name=pmc, qr_code=qr, created_user_id=created_user, modified_user_id=created_user))
        for pal in pal_list:
            number = int(number) + 1
            qr = str('{:04d}').format(number)
            insert_pal_list.append(
                Bag(name=pal, qr_code=qr, created_user_id=created_user, modified_user_id=created_user))
        Bag.objects.bulk_create(insert_pmc_list)
        Bag.objects.bulk_create(insert_pal_list)
        return JsonResponse({'message': 'success', 'status_code': 200})
    except Exception as e:
        return JsonResponse({'message': 'error:' + str(e), 'status_code': 500})


def BarCodePdfView(request):
    """
    Create barcode examples and embed in a PDF
    """
    from reportlab.lib.pagesizes import A4, legal, landscape, A3, A5, A6
    size = landscape(A4)

    result = []
    try:
        bags = Bag.objects.filter(status=1)
        for bag in bags:
            c = canvas.Canvas(PDF_ROOT + str(bag.qr_code) + '.pdf', pagesize=A5)
            barcode_value = bag.qr_code
            barcode_name = bag.name
            # draw a QR code
            qr_code = qr.QrCodeWidget(barcode_value)
            width = 10
            height = 15

            d = Drawing(45, 45, transform=[45. / width, 0, 0, 45. / height, 0, 0])
            d.add(qr_code)
            renderPDF.draw(d, c, 20, 250)

            c.setLineWidth(10)
            c.setFont('Helvetica', 50)

            # c.line(100,450,500,450)
            # c.drawString(200,400,barcode_name)
            # c.line(100,380,500,380)

            c.line(30, 220, 400, 220)
            c.drawString(120, 170, barcode_name)
            c.line(30, 150, 400, 150)

            c.save()
            result.append(bag.qr_code)
            # import pdb
            # pdb.set_trace()

        # return JsonResponse({'message':'all bags are printed','result':result ,'status_code':200})
    except Exception as e:
        print(e)
        # return JsonResponse({'message':'Only these bags are printed:', 'result':result, 'status_code':500})

    zip_file_loc = shutil.make_archive(ZIP_ROOT + 'Bags', 'zip', PDF_ROOT)
    response = HttpResponse(FileWrapper(open(zip_file_loc, 'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=Bags.zip'
    return response


class HandlerBagViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to get all the bags
    Author : Kalabha P Vinod
    Created At: 14th Feb 2018

    """
    queryset = Bag.objects.filter(status=1)
    serializer_class = BaggageListSerializer


class BaggageActionSet(CreateUpdateDeleteViewSet):
    """
    Description:  This class is used to create and edit a baggage
    Author : Kalabha P Vinod
    Created At: 15th Feb 2018

    """
    queryset = Bag.objects.all()
    serializer_class = BaggageDetailsSerializer

    def destroy(self, request, pk, **kwargs):
        Bag.objects.filter(pk=pk).update(status=0)
        return Response(status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.create(validated_data=serializer.validated_data)


class ZoneListCreateViewSet(generics.ListCreateAPIView):
    queryset = Location.objects.filter(category=1)
    serializer_class = LocSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ZoneFilter


    def create(self, request, *args, **kwargs):
        managers = request.data['managers']
        print(managers)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            req_user = User.objects.get(id=request.data['created_user_id'])
        except User.DoesNotExist:
            req_user = None
        instance = self.perform_create(serializer, managers, created_user=req_user)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def perform_create(self, serializer, managers=None, created_user=None):
        return serializer.create(validated_data=serializer.validated_data, managers=managers, created_user=created_user)


class ZoneUpdateViewSet(generics.RetrieveUpdateAPIView):
    # def retrieve(self, request, pk, **kwargs):
    #     instance = Location.objects.get(id=pk)
    #     # .prefetch_releted('managers')
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    queryset = Location.objects.filter(category=1)
    serializer_class = LocSerializer

    def update(self, request, *args, **kwargs):
        managers = request.data['managers']
        print ("manger", managers)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            req_user = User.objects.get(id=request.data['modified_user_id'])
        except User.DoesNotExist:
            req_user = None
        self.perform_update(serializer, managers, modified_user=req_user)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer, managers=None, modified_user=None):
        return serializer.update(instance=serializer.instance, validated_data=serializer.validated_data,
                                 managers=managers, modified_user=modified_user)
