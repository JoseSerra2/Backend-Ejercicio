from rest_framework import routers
from .views import SaleView
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'sales', SaleView)

urlpatterns = [
    path('', include(router.urls))
]