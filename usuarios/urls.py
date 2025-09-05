from django.urls import path, include
from .views import RoleViewSet, CustomUserViewSet, ClientViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls))
]