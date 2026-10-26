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
    class Meta:
        model = Venta
        fields = '__all__'


class DetalleVentaSerializers(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = '__all__'