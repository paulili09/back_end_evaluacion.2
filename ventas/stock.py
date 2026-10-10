from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import DetalleVenta, Producto, Venta


def actualizar_stock_venta(venta: Venta, stock_anterior: dict[int, int] | None = None):
    """Reconciles inventory with a sale inside the caller's transaction."""
    stock_anterior = stock_anterior or {}
    detalles = list(DetalleVenta.objects.filter(venta=venta))
    producto_ids = set(stock_anterior) | {detalle.producto_id for detalle in detalles}
    productos = {
        producto.id: producto
        for producto in Producto.objects.select_for_update().filter(id__in=producto_ids)
    }

    for producto_id, cantidad in stock_anterior.items():
        productos[producto_id].stock += cantidad

    cantidades_nuevas = defaultdict(int)
    for detalle in detalles:
        cantidades_nuevas[detalle.producto_id] += detalle.cantidad

    errores = []
    for producto_id, cantidad in cantidades_nuevas.items():
        producto = productos[producto_id]
        if not producto.activo:
            errores.append(f'El producto "{producto.nombre}" no está activo.')
        elif cantidad > producto.stock:
            errores.append(
                f'Stock insuficiente para "{producto.nombre}". '
                f'Disponible: {producto.stock}. Solicitado: {cantidad}.'
            )

    if errores:
        raise ValidationError(errores)

    for producto_id, cantidad in cantidades_nuevas.items():
        producto = productos[producto_id]
        producto.stock -= cantidad
        producto.save(update_fields=['stock'])


def devolver_stock_venta(venta: Venta):
    """Returns a sale's quantities to inventory before deleting it."""
    cantidades = defaultdict(int)
    for detalle in venta.detalles.all():
        cantidades[detalle.producto_id] += detalle.cantidad

    productos = Producto.objects.select_for_update().filter(id__in=cantidades)
    for producto in productos:
        producto.stock += cantidades[producto.id]
        producto.save(update_fields=['stock'])
