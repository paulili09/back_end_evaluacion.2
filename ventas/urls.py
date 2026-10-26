
from django.urls import path
from . import views

from .models import Producto, Cliente, Venta, DetalleVenta
from rest_framework import routers, serializers, viewsets

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class DetalleVentaSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleVenta
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Venta
        fields = '__all__'

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'detalles-venta', DetalleVentaViewSet)

app_name = "ventas"

urlpatterns = [
    path("ventas/", views.lista_ventas, name="listas_ventas"),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('editar/<int:pk>/', views.editar_venta, name='editar_venta'),
    path('reporte/', views.reporte_ventas, name='reporte_ventas'),
]