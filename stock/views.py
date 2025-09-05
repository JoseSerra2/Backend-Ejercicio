from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import StockMovement, Stock, MovementType
from .serializers import StockMovementSerializer, StockSerializer, MoveSerializer
from .signals import obtener_stock_mas_antiguo
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotClienteOrIsAllowedRole

class StockMovementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer

class StockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class MoveViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotClienteOrIsAllowedRole]
    queryset = MovementType.objects.all()
    serializer_class = MoveSerializer
    
class StockMasAntiguoAPIView(APIView):
    def get(self, request, product_id):
        lote = obtener_stock_mas_antiguo(product_id)
        if lote:
            serializer = StockSerializer(lote)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "No hay stock disponible para este producto."}, status=status.HTTP_404_NOT_FOUND)
    
class BorradoLogicoStockAPIView(APIView):
    def post(self, request, batch):
        try:
            stock = Stock.objects.get(batch=batch)
            stock.state = 0
            stock.save()
            return Response({'mensaje': 'Stock borrado lógicamente'})
        except Stock.DoesNotExist:
            return Response({'error': 'Stock no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Esto imprimirá el error en consola
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)