from rest_framework import routers
from .views import BrandViewSet, ProductViewSet, CategoryViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'categorys', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls))
]
