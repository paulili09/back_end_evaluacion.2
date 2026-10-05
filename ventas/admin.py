from django.contrib import admin
from .models import Producto, Venta, DetalleVenta

admin.site.site_header = "Control de Ventas - Tienda"
admin.site.site_title = "Admin Ventas"
admin.site.index_title = "Gestión Comercial y Ventas"

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'calcular_subtotal')
    readonly_fields = ('calcular_subtotal',)

    def calcular_subtotal(self, instance):
        if instance.id:
            return f"${instance.subtotal():,}"
        return "$0"
    calcular_subtotal.short_description = "Subtotal"

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'obtener_total')
    list_filter = ('fecha',)  # Filtro por rango de fechas[cite: 1]
    search_fields = ('cliente', 'id')
    inlines = [DetalleVentaInline]  # Inlines de detalle de venta[cite: 1]
    readonly_fields = ('obtener_total',)

    def obtener_total(self, obj):
        return f"${obj.total():,}"
    obtener_total.short_description = "Total ($)"

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)
