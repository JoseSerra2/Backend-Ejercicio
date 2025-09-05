from django.urls import path, include
from .views import StockMovementViewSet, StockViewSet, MoveViewSet, StockMasAntiguoAPIView, BorradoLogicoStockAPIView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'stock', StockViewSet)
router.register(r'stockmove', StockMovementViewSet)
router.register(r'move', MoveViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stock/mas-antiguo/<uuid:product_id>/', StockMasAntiguoAPIView.as_view(), name='stock-mas-antiguo'),
    path('stock/borrar-logico/<str:batch>/', BorradoLogicoStockAPIView.as_view(), name='borrado-logico-stock'),
]