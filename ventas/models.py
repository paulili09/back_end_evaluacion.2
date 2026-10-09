from django.db import models
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Producto(models.Model): 
    nombre = models.CharField(max_length=120, db_index=True) 
    sku = models.CharField(max_length=50, unique=True) 
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]) 
    stock = models.PositiveIntegerField(default=0) 
    activo = models.BooleanField(default=True) 

    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo.'})

    def __str__(self): 
        return f"{self.nombre} (${self.precio:,.0f})" 


class Cliente(models.Model): 
    nombre = models.CharField(max_length=120) 
    email = models.EmailField(blank=True, null=True) 

    def __str__(self): 
        return self.nombre 


class Venta(models.Model): 
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, blank=True, null=True) 
    fecha = models.DateTimeField(auto_now_add=True) 

    @property 
    def total(self): 
        return sum((d.subtotal for d in self.detalles.all()), Decimal('0.00'))

    def __str__(self): 
        cliente_str = self.cliente.nombre if self.cliente else "Cliente General"
        return f"Venta #{self.pk} — {cliente_str}" 


class DetalleVenta(models.Model): 
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE) 
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) 
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)]) 
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True) 

    @property 
    def subtotal(self): 
        if self.precio_unitario and self.cantidad:
            return self.cantidad * self.precio_unitario
        return Decimal('0.00')

    def clean(self):
        if self.producto_id and not self.producto.activo:
            raise ValidationError({'producto': 'El producto seleccionado no está activo.'})
        if self.producto_id and self.cantidad and self.cantidad > self.producto.stock:
            raise ValidationError({
                'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock}.'
            })

    def save(self, *args, **kwargs):
        # Asigna automáticamente el precio del producto si no viene especificado
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

    def __str__(self): 
        return f"{self.producto.nombre} x{self.cantidad}"