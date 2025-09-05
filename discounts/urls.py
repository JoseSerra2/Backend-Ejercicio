from rest_framework import routers
from .views import WhosaleDiscountViewSet, RegularDiscountViewSet, list_discountRegular_whith_product, list_wholesale_discounts_with_product
from  django.urls import path, include
router = routers.DefaultRouter()
router.register(r'who_discount', WhosaleDiscountViewSet)
router.register(r'regular_discount', RegularDiscountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('regular-discounts-with-product/', list_discountRegular_whith_product, name='regular-discounts-with-product'),
    path('who-discounts-with-product/', list_wholesale_discounts_with_product, name='who-discounts-with-product'),

]

