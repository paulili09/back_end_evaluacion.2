from rest_framework import serializers
from .models import Producto, Cliente, Venta, DetalleVenta


class ProductoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class ClienteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class VentaSerializers(serializers.ModelSerializer):
    detalles = serializers.SerializerMethodField()
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Venta
        fields = ("id", "cliente", "fecha", "detalles", "total")

    def get_detalles(self, obj):
        return DetalleVentaSerializers(
            obj.detalles.select_related("producto"), many=True
        ).data


class DetalleVentaSerializers(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = DetalleVenta
        fields = ("id", "venta", "producto", "cantidad", "precio_unitario", "subtotal")