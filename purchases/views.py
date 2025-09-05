from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema  
from .models import Purchase, PurchaseBill, PurchaseDetail, Supplier
from .serializers import PurchaseSerializer, PurchaseBillSerializer, PurchaseDetailSerializer, SupplierSerializer, PurchaseDateSerializer
from stock.serializers import  StockSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotClienteOrIsAllowedRole

class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = Supplier.objects.filter(supplier_state=1)
    serializer_class =  SupplierSerializer

    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier.supplier_state=0
        supplier.save()
        return Response({'Se ha eliminado el Proveedor correctamente'}, status=status.HTTP_200_OK)
    
    

class PurchaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = Purchase.objects.filter(purchase_state=1)
    serializer_class = PurchaseSerializer
    def destroy(self, request, *args, **kwargs):
        purchase = self.get_object()
        purchase.purchase_state=0
        purchase.save()
        return Response({'Se ha eliminado la compra correctamente'}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        method='post',
        request_body=PurchaseDateSerializer,
        responses={200: PurchaseSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='dates_report')
    def report_date(self, request):
        serializer = PurchaseDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        initial_date = serializer.validated_data.get('initial_date')
        final_date = serializer.validated_data.get('final_date')

        if initial_date and final_date:
            purchases = Purchase.objects.filter(
                purchase_date__gte=initial_date,
                purchase_date__lte=final_date
            )
        else:
            purchases = Purchase.objects.all()

        output_serializer = self.get_serializer(purchases, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

class RegisterPurchaseView(APIView):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    @swagger_auto_schema(
        operation_description= 'Registrar compra completa',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'purchase': openapi.Schema(
                    type=openapi.TYPE_OBJECT, 
                    description="Datos de la compra",
                    properties={
                        'purchase_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la compra'),
                        'supplier': openapi.Schema(type=openapi.TYPE_STRING, description='ID del proveedor')
                    },
                    required=['purchase_date', 'supplier']
                ),
                'details': openapi.Schema(
                    type=openapi.TYPE_ARRAY, 
                    description="Detalles de la compra", 
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cantidad'),
                            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal', description='Preico Unitario'),
                            'product': openapi.Schema(type=openapi.TYPE_STRING, description='ID de producto'),
                            'expire_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de expiracion del producto')
                        },
                        required=['quantity', 'unit_price',  'product', 'expire_date']
                    )
                ),
                'bill': openapi.Schema(
                    type=openapi.TYPE_OBJECT, 
                    description='Datos de la factura',
                    properties={
                        'bill_number': openapi.Schema(type=openapi.TYPE_STRING, description='No de la factura'),
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la compra'),
                        'discount': openapi.Schema(type=openapi.TYPE_NUMBER, format= 'decimal', description='Descuento aplicado', default=0, nullable= True)
                    },
                    required=['bill_number', 'date'],
                )
            },
            required=['purchase', 'details', 'bill'],
        ),
        responses={
            201: 'Compra registrada correctamente', 
            400: 'Error en los datos'
        }
    )
    @transaction.atomic
    def post(self, request):
        print("Entro al post")
        data = request.data 

        #Purchase
        purchase_data= data.get('purchase')
        purchase_serializer = PurchaseSerializer(data=purchase_data)
        purchase_serializer.is_valid(raise_exception=True)
        purchase =purchase_serializer.save(purchase_total=0, purchase_state=1)

        #PurchaseDetail
        total=0
        for detail in data.get('details', []):
            detail['purchase'] = purchase.purchase_id
            print("Detalle enviado al serializer:", detail)
            detail_serializer= PurchaseDetailSerializer(data=detail)
            detail_serializer.is_valid(raise_exception=True)
            detail_obj = detail_serializer.save()

            total+=detail_obj.quantity * float(detail_obj.unit_price)

            #Stock
            stock_data = {
            "initial_amount": detail_obj.quantity,
            "current_amount": detail_obj.quantity,
            "expire_date": detail.get("expire_date"),
            "state": 1,
            "product_id": detail_obj.product.product_id
            }

            stock_serializer= StockSerializer(data=stock_data)
            stock_serializer.is_valid(raise_exception=True)
            stock_serializer.save()

        purchase.purchase_total = total
        purchase.save()

        #PBill
        bill_data = data.get('bill')
        if bill_data:
            bill_data['purchase'] = purchase.purchase_id

            discount= float(bill_data.get('discount', 0) or 0)
            bill_total = total - discount

            bill_data['total'] = bill_total if bill_total> 0 else 0 

            bill_serializer=PurchaseBillSerializer(data=bill_data)
            if not bill_serializer.is_valid():
                print("Error en factura:", bill_serializer.errors)
                return Response({'errors': bill_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
            bill_serializer.save()
        print("Paso todo")
        return Response({'message': 'Compra registrada correctamente'}, status=status.HTTP_201_CREATED)

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = PurchaseDetail.objects.filter(purchase_detail_state=1)
    serializer_class = PurchaseDetailSerializer
    def destroy(self, request, *args, **kwargs):
        purchase_detail = self.get_object()
        purchase_detail.purchase_detail_state=0
        purchase_detail.save()
        return Response({'Se ha eliminado el detalle de compra correctamente'}, status=status.HTTP_200_OK)


class PurchaseBillViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = PurchaseBill.objects.filter(purchase_bill_state=1)
    serializer_class = PurchaseBillSerializer
    def destroy(self, request, *args, **kwargs):
        purchase_bill = self.get_object()
        purchase_bill.purchase_bill_state=0
        purchase_bill.save()
        return Response({'Se ha eliminado la factura de compra correctamente'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def purchase_list_with_supplier_name(request):
    purchases = Purchase.objects.select_related('supplier').filter(purchase_state=1)
    data = [
        {
            'purchase_id': str(p.purchase_id),
            'purchase_total': float(p.purchase_total),
            'purchase_date': p.purchase_date.isoformat(),
            'supplier_name': p.supplier.supplier_name,
        }
        for p in purchases
    ]
    return Response(data)

@api_view(['GET'])
def get_purchase_detail(request,purchase_id):
    purchase = Purchase.objects.select_related('supplier').get(purchase_id=purchase_id)
    details = PurchaseDetail.objects.select_related('product').filter(purchase=purchase)

    data = {
        'purchase_id': str(purchase.purchase_id),
        'purchase_date': purchase.purchase_date,
        'purchase_total': float(purchase.purchase_total),
        'supplier': {
            'name': purchase.supplier.supplier_name,
            'phone': purchase.supplier.phone_number,
            'email': purchase.supplier.email,
            'nit': purchase.supplier.nit,
        },
        'products': [
            {
                'product_name': d.product.product_name,
                'quantity': d.quantity,
                'unit_price': float(d.unit_price),
                'subtotal': float(d.quantity * d.unit_price),
                'expire_date': d.expire_date,
            }
            for d in details
        ]
    }

    return Response(data)

class UpdatePurchaseView(APIView):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]

    @swagger_auto_schema(
        operation_description="Actualizar una compra completa",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'purchase': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Datos de la compra",
                    properties={
                        'purchase_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la compra'),
                        'supplier': openapi.Schema(type=openapi.TYPE_STRING, description='ID del proveedor')
                    },
                    required=['purchase_date', 'supplier']
                ),
                'details': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Detalles de la compra",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'purchase_detail_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID del detalle existente, opcional si es nuevo'),
                            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cantidad'),
                            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal', description='Precio unitario'),
                            'product': openapi.Schema(type=openapi.TYPE_STRING, description='ID del producto'),
                            'expire_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de expiración')
                        },
                        required=['quantity', 'unit_price', 'product', 'expire_date']
                    )
                ),
                'bill': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Datos de la factura',
                    properties={
                        'bill_number': openapi.Schema(type=openapi.TYPE_STRING, description='No de la factura'),
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la factura'),
                        'discount': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal', description='Descuento aplicado', default=0, nullable=True)
                    },
                    required=['bill_number', 'date']
                )
            },
            required=['purchase', 'details', 'bill']
        ),
        responses={200: 'Compra actualizada correctamente', 400: 'Error en los datos', 404: 'Compra no encontrada'}
    )
    @transaction.atomic
    def put(self, request, purchase_id):
       
        try:
            purchase = Purchase.objects.get(purchase_id=purchase_id, purchase_state=1)
        except Purchase.DoesNotExist:
            return Response({'error': 'Compra no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

   
        purchase_data = data.get('purchase', {})
        purchase_serializer = PurchaseSerializer(purchase, data=purchase_data, partial=True)
        purchase_serializer.is_valid(raise_exception=True)
        purchase_serializer.save()

    
        total = 0
        details_data = data.get('details', [])
        for detail in details_data:
            detail_id = detail.get('purchase_detail_id')
            if detail_id:
              
                detail_obj = PurchaseDetail.objects.get(purchase_detail_id=detail_id)
                detail_serializer = PurchaseDetailSerializer(detail_obj, data=detail, partial=True)
            else:
             
                detail['purchase'] = str(purchase.purchase_id)
                detail_serializer = PurchaseDetailSerializer(data=detail)

            detail_serializer.is_valid(raise_exception=True)
            detail_obj = detail_serializer.save()

            total += detail_obj.quantity * float(detail_obj.unit_price)

          
            stock_data = {
                "initial_amount": detail_obj.quantity,
                "current_amount": detail_obj.quantity,
                "expire_date": detail.get("expire_date"),
                "state": 1,
                "product_id": detail_obj.product.product_id
            }
            stock_serializer = StockSerializer(data=stock_data)
            stock_serializer.is_valid(raise_exception=True)
            stock_serializer.save()

      
        purchase.purchase_total = total
        purchase.save()

        
        bill_data = data.get('bill')
        if bill_data:
            if 'total' not in bill_data:
                bill_data['total'] = total

            bill_number = bill_data.get('bill_number')
            if bill_number:
                try:
                    bill = PurchaseBill.objects.get(bill_number=bill_number)
                    bill_serializer = PurchaseBillSerializer(bill, data=bill_data, partial=True)
                except PurchaseBill.DoesNotExist:
                    bill_serializer = PurchaseBillSerializer(data=bill_data)
            else:
                
                bill_serializer = PurchaseBillSerializer(data=bill_data)

            bill_serializer.is_valid(raise_exception=True)
            bill_serializer.save()

        return Response({'message': 'Compra actualizada correctamente'}, status=status.HTTP_200_OK)