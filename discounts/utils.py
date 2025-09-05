from datetime import date
from .models import RegularDiscount, WholesaleDiscount
from django.db.models import Q 

def get_discounts(product_id, quantity=1):
    today = date.today()

    wholesale = WholesaleDiscount.objects.filter(
        product_id=product_id,
        w_state= 1, 
        min_quantity__lte=quantity,
    ).filter(
        Q(max_quantity__gte=quantity) | Q(max_quantity__isnull=True)
    ).first()

    if wholesale and quantity >= wholesale.min_quantity:
        return{
            "Tipo": "Mayoreo",
            "Precio Unitario": float(wholesale.unit_price),
            "Cantidad minima": wholesale.min_quantity,
            "Cantidad maxima": wholesale.max_quantity

        }
    
    regular = RegularDiscount.objects.filter(
        product_id=product_id,
        discount_state=1,
        initial_date__lte =today
    ).filter(
        Q(final_date__gte=today) | Q(final_date__isnull=True)
    ).first()

    if regular:
        return{
            "Tipo": "Regular",
            "Porcentaje": regular.percentage
        }
    return None