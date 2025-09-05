from rest_framework import serializers
from stock.signals import obtener_stock_mas_antiguo
from .models import Sale, SaleDetail, SaleBill
from products.models import Product 
from usuarios.models import Client
from django.db import transaction
from usuarios.serializers import ClientSerializer
from products.serializer import ProductSerializer
from discounts.utils import get_discounts
from decimal import Decimal

class SaleDetailSerializer(serializers.ModelSerializer):

    product_data = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    product= ProductSerializer(read_only=True)

    class Meta:
        model = SaleDetail
        fields = ['quantity', 'product', 'product_data', 'sale_detail_id', 'unit_price', 'unit_discount', 'sale_state', 'subtotal', 'discount_subtotal', 'sale', 'created_at', 'updated_at' ]
        read_only_fields = ['sale_detail_id', 'unit_price', 'unit_discount', 'sale_state', 'subtotal', 'discount_subtotal', 'sale', 'created_at', 'updated_at', 'product']

class SaleBillSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only = True)
    class Meta:
        model = SaleBill
        fields = '__all__'
        read_only_fields = ['bill_id', 'subtotal', 'total_discount', 'total', 'sale', 'sale_state', 'client']

class ReportDateSerializer(serializers.Serializer):
    initial_date = serializers.DateField(required=False, allow_null=True)
    final_date = serializers.DateField(required=False, allow_null=True)

class SaleSerializer(serializers.ModelSerializer):
    details = SaleDetailSerializer(many = True) 
    #bill = SaleBillSerializer(read_only=True)
    nit = serializers.CharField(write_only=True, required=False)


    class Meta:
        model = Sale
        fields = ['sale_id', 'sale_date', 'subtotal', 'total_discount', 'total', 'sale_state', 'created_at', 'updated_at','details', 'nit']
        read_only_fields = ['sale_id', 'subtotal', 'total_discount', 'total', 'sale_state', 'sale_date']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        bill = SaleBill.objects.filter(sale=instance).first()
        data['bill'] = SaleBillSerializer(bill).data if bill else None
        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        client_nit = validated_data.pop('nit', None)

        with transaction.atomic():
            total = 0
            total_discount_sale = 0
            subtotal_sale = 0

            sale = Sale.objects.create(total = 0, subtotal = 0, total_discount = 0, **validated_data)

            for detail_data in details_data:

                qty = detail_data['quantity']
                product = detail_data['product_data']
                discount = get_discounts(product, qty)
                price = product.unit_price
                unit_discount = 0.0
                if discount:
                    discount_type = discount['Tipo']
                    if(discount_type == "Regular"):
                        percentage = discount['Porcentaje']
                        unit_discount = price * percentage
                    else:
                        unit_price_discount = Decimal(str(discount.get('Precio Unitario', price)))
                        unit_discount = (price - unit_price_discount).quantize(Decimal('0.01'))

                discount_subtotal = 0
                discount_subtotal += unit_discount * qty
                subtotal = price * detail_data['quantity']
                quantity_needed = detail_data['quantity']
                remaining_qty = quantity_needed

                while remaining_qty > 0:
                    lote = obtener_stock_mas_antiguo(product.product_id)

                    if not lote:
                        raise serializers.ValidationError(f"No hay suficiente stock disponible para {product.product_name}")

                    qty_to_deduct = min(remaining_qty, lote.current_amount)
                    lote.current_amount -= qty_to_deduct
                    lote.save()  

                    subtotal_sale += subtotal

                    SaleDetail.objects.create(
                        quantity = detail_data['quantity'],
                        product = product,
                        unit_price = price,
                        unit_discount = unit_discount, #agregar descuento unitario del producto
                        subtotal = subtotal, #subtotal sin el descuento
                        discount_subtotal = discount_subtotal, #total del descuento
                        sale = sale
                    )
                    total_discount_sale += Decimal(discount_subtotal)
                    remaining_qty -= qty_to_deduct
                    
            total = subtotal_sale - total_discount_sale
            sale.subtotal = subtotal_sale
            sale.total = total
            sale.total_discount = total_discount_sale
            client_bill = Client.objects.filter(nit = client_nit).first()
            sale.save()

            SaleBill.objects.create(
                total_discount = total_discount_sale,
                total = total,
                subtotal = subtotal_sale,
                sale = sale,
                date = sale.sale_date,
                client = client_bill
            )
        return sale

if __name__ == "__main__":
    numero = 25
    if numero % 2 == 0:
        print(f"El número {numero} es par")
        for i in range(5):
            print(f"Iteración {i+1}: todavía es par")
    else:
        print(f"El número {numero} es impar")
        suma = 0
        for i in range(1, 6):
            suma += i
            print(f"Suma parcial en la vuelta {i}: {suma}")
        print(f"La suma final es: {suma}")



