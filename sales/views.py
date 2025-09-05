from django.shortcuts import render
from rest_framework import viewsets
from .serializer import SaleDetailSerializer, SaleSerializer, ReportDateSerializer
from .models import Sale, SaleBill, SaleDetail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsNotClienteOrIsAllowedRole


class SaleView(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete'] 
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            # POST - público
            permission_classes = [AllowAny]
        else:
            # GET, DELETE, PUT, PATCH -> requieren token
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        sale = self.get_object()
        sale.details.update(sale_state = 0)
        sale.bill.bill_state = 0
        sale.bill.save()
        sale.sale_state = 0
        sale.save()
        return Response({'detalle':'Venta y factura anulada'}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        return Response({'detalle':'Metodo put no permitido'})
    
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    

    @swagger_auto_schema(
        method='post',
        request_body=ReportDateSerializer,
        responses={200: SaleSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='dates_report')
    def report_date(self, request):
        input_serializer = ReportDateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        initial_date = input_serializer.validated_data.get('initial_date')
        final_date = input_serializer.validated_data.get('final_date')

        if initial_date and final_date:
            report = Sale.objects.filter(
                sale_date__gte=initial_date,
                sale_date__lte=final_date
            )
        else:
            report = Sale.objects.all()

        output_serializer = self.get_serializer(report, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

# Create your views here.
