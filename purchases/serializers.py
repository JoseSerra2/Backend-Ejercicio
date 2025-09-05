from rest_framework import serializers
from .models import Supplier, Purchase, PurchaseDetail, PurchaseBill
from products.models import Product
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields  = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_total= serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    purchase_state=serializers.IntegerField(read_only=True)
    class Meta:
        model= Purchase 
        fields = '__all__'

class PurchaseDetailSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = PurchaseDetail
        fields = '__all__'

    def create(self, validated_data):
        product_id = validated_data.pop('product')
        print("objeto producto: ", product_id)
        validated_data['product'] = Product.objects.get(pk=product_id.product_id)
        return super().create(validated_data)


class PurchaseDateSerializer(serializers.Serializer):
    initial_date = serializers.DateField(required=True)
    final_date = serializers.DateField(required=True)
    
class PurchaseBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseBill
        fields = '__all__'