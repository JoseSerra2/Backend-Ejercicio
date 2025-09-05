from django.shortcuts import render
from rest_framework import viewsets
from .models import Brand, Product, Category
from .serializer import BrandSerializer, CategorySerializer, ProductSerializer
from discounts.models import RegularDiscount, WholesaleDiscount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsNotClienteOrIsAllowedRole

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active_category']:
            # GET - Publicos
            permission_classes = [AllowAny]
        else:
            # DELETE, PUT, POST, PATCH -> requieren token
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        brand = self.get_object()
        brand.brand_state = 0
        brand.save()
        return Response({'detalle':'Marca desactivada'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='active', permission_classes=[AllowAny])
    def active_category(self, request, *args, **kwargs):
        brands = Brand.objects.filter(brand_state = 1)
        serializer = self.get_serializer(brands, many = True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='activate_brand')
    def activate_brand(self, request, *args, **kwargs):
        brand = self.get_object()
        brand.brand_state = 1
        brand.save()
        return Response({'detalle':'Marca activada'}, status= status.HTTP_202_ACCEPTED)
    

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active_category']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category.category_state = 0
        category.save()
        return Response({'detalle':'Categoria desactivada'}, status = status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='active', permission_classes=[AllowAny])
    def active_category(self, request, *args, **kwargs):
        categories = Category.objects.filter(category_state = 1)
        serializer = self.get_serializer(categories, many = True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['patch'], url_path='activate_category')
    def activate_category(self, request, *args, **kwargs):
        category = self.get_object()
        category.category_state = 1
        category.save()
        return Response({'detalle':'Categoría activada'}, status= status.HTTP_202_ACCEPTED)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'catalog_products']:
            # GET - Publicos
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.product_state = 0
        product.save()
        return Response({'detalle':'Producto desactivad0'}, status = status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='activate_product')
    def activate_product(self, request, *args, **kwargs):
        product = self.get_object()
        product.product_state = 1
        product.save()
        return Response({'detalle':'Producto activado'}, status= status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'], url_path='catalog_products', permission_classes=[AllowAny])
    def catalog_products(self, request, *args, **kwargs):
        today = timezone.now().date() 
        active_discounts = RegularDiscount.objects.filter(discount_state=1).filter(
            Q(initial_date__lte=today),
            Q(final_date__isnull=True) | Q(final_date__gte=today)
        )

        print(active_discounts)
        products = Product.objects.filter(product_state = 1, current_stock__gt = 0).prefetch_related(
            Prefetch(
                'regular_discount',
                queryset=active_discounts,
                to_attr='active_regular_discounts' 
            )   
        )
        serializer = self.get_serializer(products, many = True)
        return Response(serializer.data)
