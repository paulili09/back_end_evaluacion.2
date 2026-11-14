from collections import defaultdict

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import routers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Producto, Cliente, Venta, DetalleVenta
from .serializers import (
    ProductoSerializers,
    ClienteSerializers,
    VentaSerializers,
    DetalleVentaSerializers,
)
from .stock import actualizar_stock_venta, devolver_stock_venta


def cantidades_de_venta(venta):
    """Devuelve {id_producto: cantidad} de lo que tiene la venta ahora."""
    cantidades = defaultdict(int)
    for detalle in venta.detalles.all():
        cantidades[detalle.producto_id] += detalle.cantidad
    return dict(cantidades)


def aplicar_cambio_con_stock(venta, accion):
    """Hace el cambio (crear/editar/borrar) y ajusta el stock.
    Si algo falla (stock insuficiente, producto inactivo), se deshace todo."""
    anterior = cantidades_de_venta(venta)
    try:
        with transaction.atomic():
            accion()
            actualizar_stock_venta(venta, anterior)
    except DjangoValidationError as error:
        raise ValidationError(error.messages)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by("nombre")
    serializer_class = ProductoSerializers
    permission_classes = [IsAuthenticated]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nombre")
    serializer_class = ClienteSerializers
    permission_classes = [IsAuthenticated]


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.select_related("cliente").prefetch_related(
        "detalles__producto"
    ).order_by("-fecha")
    serializer_class = VentaSerializers
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Al borrar una venta, el stock vuelve al producto
        with transaction.atomic():
            devolver_stock_venta(instance)
            instance.delete()


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.select_related("venta", "producto").all()
    serializer_class = DetalleVentaSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        venta = serializer.validated_data["venta"]
        aplicar_cambio_con_stock(venta, serializer.save)

    def perform_update(self, serializer):
        venta = serializer.instance.venta
        nueva_venta = serializer.validated_data.get("venta")
        if nueva_venta and nueva_venta != venta:
            raise ValidationError(
                {"venta": "No se puede mover un detalle a otra venta."}
            )
        aplicar_cambio_con_stock(venta, serializer.save)

    def perform_destroy(self, instance):
        aplicar_cambio_con_stock(instance.venta, instance.delete)


# Router para registrar todas las rutas automáticamente
router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'detalles-venta', DetalleVentaViewSet)