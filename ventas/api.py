from rest_framework import routers, viewsets
from .models import Producto, Cliente, Venta, DetalleVenta
from .serializers import (
    ProductoSerializers, 
    ClienteSerializers, 
    VentaSerializers, 
    DetalleVentaSerializers
)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by("nombre")
    serializer_class = ProductoSerializers


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nombre")
    serializer_class = ClienteSerializers


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.select_related("cliente").prefetch_related(
        "detalles__producto"
    ).order_by("-fecha")
    serializer_class = VentaSerializers


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.select_related("venta", "producto").all()
    serializer_class = DetalleVentaSerializers


# Router para registrar todas las rutas automáticamente
router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'detalles-venta', DetalleVentaViewSet)