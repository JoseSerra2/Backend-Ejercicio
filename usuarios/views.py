from rest_framework import viewsets
from .models import Role, CustomUser, Client
from .serializers import RoleSerializer, CustomUserSerializer, ClientSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsNotClienteOrIsAllowedRole
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            #GET - GET {ID} - Publicos
            permission_classes = [AllowAny]
        else:
            #DELETE, PUT, POST, PATCH TOKEN
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'me']:
            # GET y POST -> público
            permission_classes = [AllowAny]
        else:
            # DELETE, PUT, PATCH -> requieren token
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        public_actions = {'create', 'search_by_nit'}
        if self.action in public_actions:
            # POST -> público
            permission_classes = [AllowAny]
        else:
            # DELETE, PUT, PATCH -> requieren token
            permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], url_path='search_by_nit',  permission_classes=[AllowAny])
    def search_by_nit(self, request):
        nit = request.query_params.get('nit')
        if not nit:
            return Response({'error':'Debe proporcionar un NIT'}, status=400)
        client = Client.objects.filter(nit=nit).first()
        if not client:
            return Response({'message':'No encontrado'}, status=404)
        return Response(self.get_serializer(client).data)
