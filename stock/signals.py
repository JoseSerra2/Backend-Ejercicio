from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Stock, StockMovement, MovementType
from products.models import Product
from datetime import date
from django.db.models import Q
from sales.models import Sale, SaleDetail
from purchases.models import Purchase, PurchaseDetail
from products.models import Product 


#Antigua creacion de stock
#@receiver(post_save, sender=Stock)
#def crear_movimiento_entrada(sender, instance, created, **kwargs):
#    if created:
#        try:
#            entrada_type = MovementType.objects.get(movement_type__iexact="entrada")
#        except MovementType.DoesNotExist:
#            entrada_type = MovementType.objects.create(movement_type="Entrada", state=1)
#
#        StockMovement.objects.create(
#            direction=StockMovement.Direction.ENTRADA,
#            date=date.today(),
#            quantity=instance.initial_amount,
#            batch=instance,
#            movement_type=entrada_type,
#            state=1,
#            observations="Movimiento automatico por creacion de stock"
#        )
        
def revisar_lote(stock_instance):
    hoy = date.today()

    if stock_instance.state == 0:
        return  

    motivo = None
    if stock_instance.expire_date and stock_instance.expire_date < hoy:
        motivo = "Vencido"
    elif stock_instance.current_amount == 0:
        motivo = "Vacio"

    #realiza el movimiento si en dado caso esta vencido o vacio
    if motivo:
        try:
            mov_type = MovementType.objects.get(movement_type__iexact=motivo)
        except MovementType.DoesNotExist:
            mov_type = MovementType.objects.create(movement_type=motivo, state=1)

        StockMovement.objects.create(
            direction=StockMovement.Direction.SALIDA,
            date=hoy,
            quantity=0,
            batch=stock_instance,
            movement_type=mov_type,
            state=1,
            observations=f"Movimiento automatico por lote {motivo.lower()}"
        )

        stock_instance.state = 0
        stock_instance.save(update_fields=["state"])
        
from .models import Stock

def obtener_stock_mas_antiguo(product_id):
    return (
        Stock.objects.filter(product_id=product_id, state=1, current_amount__gt=0).filter(Q(expire_date__gte=date.today()) | Q(expire_date__isnull=True))
        .order_by("expire_date")
        .first()
    )
    
@receiver(post_save, sender=SaleDetail)
def descontar_stock(sender, instance, created, **kwargs):
    if not created:
        return

    producto = instance.product
    cantidad_restante = instance.quantity
    fecha_venta = instance.sale.sale_date

    try:
        tipo_mov = MovementType.objects.get(movement_type__iexact="Salida por venta")
    except MovementType.DoesNotExist:
        tipo_mov = MovementType.objects.create(movement_type="Salida por venta", state=1)

    lotes_disponibles = Stock.objects.filter(
        product=producto, state=1, current_amount__gt=0
    ).order_by('expire_date', 'created_at')

    for lote in lotes_disponibles:
        if cantidad_restante <= 0:
            break

        disponible = lote.current_amount
        cantidad_a_descontar = min(cantidad_restante, disponible)

        StockMovement.objects.create(
            direction=StockMovement.Direction.SALIDA,
            date=fecha_venta,
            quantity=cantidad_a_descontar,
            batch=lote,
            movement_type=tipo_mov,
            state=1,
            observations=f"Salida por venta {instance.sale.sale_id}",
            sale_reference=instance
        )
        producto = instance.product
        producto.current_stock -= cantidad_a_descontar 
        producto.save(update_fields=["current_stock"])

        lote.current_amount -= cantidad_a_descontar
        if lote.current_amount == 0:
            lote.state = 0
        lote.save(update_fields=["current_amount", "state"])
        cantidad_restante -= cantidad_a_descontar

def obtener_stock_mas_antiguo(product_id):
    return (
        Stock.objects.filter(product_id=product_id, state=1, current_amount__gt=0)
        .order_by("expire_date")
        .first()
    )
    
@receiver(post_save, sender=SaleDetail)
def descontar_stock(sender, instance, created, **kwargs):
    if not created:
        return

    producto = instance.product
    cantidad_restante = instance.quantity
    fecha_venta = instance.sale.sale_date

    try:
        tipo_mov = MovementType.objects.get(movement_type__iexact="Salida por venta")
    except MovementType.DoesNotExist:
        tipo_mov = MovementType.objects.create(movement_type="Salida por venta", state=1)

    lotes_disponibles = Stock.objects.filter(
        product=producto, state=1, current_amount__gt=0
    ).order_by('expire_date', 'created_at')

    for lote in lotes_disponibles:
        if cantidad_restante <= 0:
            break

        disponible = lote.current_amount
        cantidad_a_descontar = min(cantidad_restante, disponible)

        StockMovement.objects.create(
            direction=StockMovement.Direction.SALIDA,
            date=fecha_venta,
            quantity=cantidad_a_descontar,
            batch=lote,
            movement_type=tipo_mov,
            state=1,
            observations=f"Salida por venta {instance.sale.sale_id}",
            sale_reference=instance
        )
        producto = instance.product
        producto.current_stock -= cantidad_a_descontar 
        producto.save(update_fields=["current_stock"])

        lote.current_amount -= cantidad_a_descontar
        if lote.current_amount == 0:
            lote.state = 0
        lote.save(update_fields=["current_amount", "state"])
        cantidad_restante -= cantidad_a_descontar

    if cantidad_restante > 0:
        print(f"Stock insuficiente para el producto {producto.product_name}. Faltaron {cantidad_restante} unidades.")
        
@receiver(post_save, sender=PurchaseDetail)
def crear_stock_y_movimiento_por_compra(sender, instance, created, **kwargs):
    if not created:
        return
    
    print(f"[DEBUG] Se creó detalle de compra: {instance.purchase.purchase_id}")

    try:
        tipo_mov = MovementType.objects.get(movement_type__iexact="Entrada por compra")
    except MovementType.DoesNotExist:
        tipo_mov = MovementType.objects.create(movement_type="Entrada por compra", state=1)

    producto = instance.product
    cantidad = instance.quantity
    vencimiento = instance.expire_date

    producto.current_stock += cantidad 
    producto.save(update_fields=["current_stock"])
    stock = Stock.objects.create(
        initial_amount=cantidad,
        current_amount=cantidad,
        expire_date=vencimiento,
        state=1,
        product=producto
    )

    movimiento = StockMovement.objects.create(
        direction=StockMovement.Direction.ENTRADA,
        date=instance.purchase.purchase_date,
        quantity=cantidad,
        batch=stock,
        movement_type=tipo_mov,
        state=1,
        observations=f"Entrada por compra {instance.purchase.purchase_id}",
        purchase_reference= instance
    )

    print(f"[DEBUG] Movimiento creado: {movimiento.movement_id}")
    
@receiver(post_save, sender=StockMovement)
def descontar_stock_manual(sender, instance, created, **kwargs):
    if not created:
        return

    # Solo para movimientos de salida
    if instance.direction == StockMovement.Direction.SALIDA:
        lote = instance.batch
        if lote.current_amount >= instance.quantity:
            lote.current_amount -= instance.quantity
            # Si stock llega a 0, cambia estado
            if lote.current_amount == 0:
                lote.state = 0
            lote.save(update_fields=['current_amount', 'state'])
        else:
            # Aquí puedes decidir si lanzar error o solo advertir
            print(f"Stock insuficiente en lote {lote.batch} para descontar {instance.quantity} unidades.")
            
@receiver(post_save, sender=Stock)
def crear_movimiento_borrado_logico(sender, instance, created, **kwargs):
    if created:
        return

    if instance.state == 0:
        mov_type, _ = MovementType.objects.get_or_create(
            movement_type__iexact="Borrado lógico",
            defaults={"movement_type": "Borrado lógico", "state": 1}
        )

        existe = StockMovement.objects.filter(
            batch=instance,
            movement_type=mov_type,
            date=date.today(),
            observations__icontains="borrado lógico"
        ).exists()

        if not existe:
            StockMovement.objects.create(
                direction=StockMovement.Direction.SALIDA,  # Salida por borrado lógico
                date=date.today(),
                quantity=instance.current_amount,  # Puede ser la cantidad actual antes de "borrar"
                batch=instance,
                movement_type=mov_type,
                state=1,
                observations=f"Movimiento automático por borrado lógico del lote {instance.batch}"
            )
