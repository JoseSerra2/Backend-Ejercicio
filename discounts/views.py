from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from .models import RegularDiscount, WholesaleDiscount
from .serializers import RegularDiscountSerializer, WholesaleDiscountSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import get_discounts
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotClienteOrIsAllowedRole

class RegularDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = RegularDiscount.objects.filter(discount_state=1)
    serializer_class = RegularDiscountSerializer
    def destroy(self, request, *args, **kwargs):
        regular_discount = self.get_object()
        regular_discount.discount_state=0
        regular_discount.save()
        return  Response({'Se ha eliminado el Descuento regular correctamente'}, status=status.HTTP_200_OK)
    
class WhosaleDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = WholesaleDiscount.objects.filter(w_state=1)
    serializer_class = WholesaleDiscountSerializer
    def destroy(self, request, *args, **kwargs):
        who_discount = self.get_object()
        who_discount.w_state = 0
        who_discount.save()
        return Response({'Se ha eliminado correctamente el descuento'})

@api_view(['GET'])
def list_discountRegular_whith_product(request, product_id):
    regular_discounts = RegularDiscount.objects.filter(product_id=product_id, discount_state=1)
    regular_data = RegularDiscountSerializer(regular_discounts, many=True).data

    return Response({
        "regular_discounts": regular_data
    })

@api_view(['GET'])
def list_discountRegular_whith_product(request):
    discounts = RegularDiscount.objects.select_related('product').filter(discount_state=1)

    data = []
    for d in discounts:
        data.append({
            'discount_id': str(d.discount_id),
            'discount_name': d.discount_name,
            'discount_description': d.discount_description,
            'percentage': float(d.percentage),
            'initial_date': d.initial_date,
            'final_date': d.final_date,
            'product_name': d.product.product_name,
            'product_id': str(d.product.product_id)

        })

    return Response({'regular_discounts': data})

@api_view(['GET'])
def list_wholesale_discounts_with_product(request):
    wholesale_discounts = WholesaleDiscount.objects.select_related('product').filter(w_state=1)

    data = []
    for d in wholesale_discounts:
        data.append({
            "wholesale_discount_id": str(d.wholesale_discount_id),
            "min_quantity": d.min_quantity,
            "max_quantity": d.max_quantity,
            "unit_price": float(d.unit_price),
            "product_name": d.product.product_name,
            "product_id": str(d.product.product_id)
        })

    return Response({"wholesale_discounts": data})