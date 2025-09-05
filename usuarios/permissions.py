# yourapp/permissions.py
from rest_framework.permissions import BasePermission

class IsNotClienteOrIsAllowedRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        user_role_name = user.role.role.lower() if user.role else ""
        return user_role_name != "cliente"
