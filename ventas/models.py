from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.nombre} (${self.precio:,})"

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=100, blank=True, null=True)

    def total(self):
        return sum(item.subtotal() for item in self.detalles.all())
    
    total.short_description = 'Total Venta'

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.IntegerField(validators=[MinValueValidator(0)], blank=True)

    def subtotal(self):
        return self.cantidad * self.precio_unitario if self.precio_unitario else 0

    def save(self, *args, **kwargs):
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
