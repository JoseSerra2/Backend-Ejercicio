from rest_framework import routers
from .views import (
    PurchaseViewSet,
    SupplierViewSet,
    PurchaseDetailViewSet,
    PurchaseBillViewSet,
    RegisterPurchaseView,
    purchase_list_with_supplier_name ,
    get_purchase_detail,
    UpdatePurchaseView
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'purchases', PurchaseViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'purchase_detail', PurchaseDetailViewSet)
router.register(r'purchase_bill', PurchaseBillViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registerPurchase/', RegisterPurchaseView.as_view(), name='register-purchase'),  
    path('purchases-with-supplier/', purchase_list_with_supplier_name, name='purchases_with_supplier'),
    path('get-purchase-detail/<uuid:purchase_id>', get_purchase_detail, name='purchase_detail'),
    path('update-total/<uuid:purchase_id>/', UpdatePurchaseView.as_view(), name='update_purchase_total'),

]
