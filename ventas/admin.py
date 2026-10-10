from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse
from django.db import transaction
import csv
from .models import Producto, Cliente, Venta, DetalleVenta
from .stock import actualizar_stock_venta, devolver_stock_venta

# 1. Branding del espacio Django Admin (Cumple requisito de branding)
admin.site.site_header = "Control de Ventas — Tienda"
admin.site.site_title = "Admin Ventas"
admin.site.index_title = "Gestión de Productos y Registro de Ventas"


# 2. Validación de Inlines (Comprueba stock antes de guardar)
class DetalleVentaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            prod = form.cleaned_data.get('producto')
            cant = form.cleaned_data.get('cantidad')
            if prod and cant:
                disponible = prod.stock
                if form.instance.pk and form.instance.producto_id == prod.id:
                    disponible += form.instance.cantidad
                if cant > disponible:
                    raise ValidationError(
                        f"Stock insuficiente para {prod.nombre}. Disponible: {disponible}."
                    )


# 3. Inline para Detalle de Venta (Cumple requisito de Caso 2)[cite: 1]
class DetalleVentaInline(admin.TabularInline): 
    model = DetalleVenta 
    extra = 1 
    formset = DetalleVentaInlineFormSet
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ("subtotal",) 


# 4. Acción para reporte básico en CSV (Cumple reporte/exportación del Admin)[cite: 1]
@admin.action(description="Exportar ventas seleccionadas a CSV (Reporte)") 
def exportar_ventas_csv(modeladmin, request, queryset): 
    response = HttpResponse(content_type='text/csv') 
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"' 
    writer = csv.writer(response) 
    writer.writerow(["ID Venta", "Cliente", "Fecha", "Total"])   
    for v in queryset.select_related('cliente').prefetch_related('detalles__producto'): 
        cliente_nombre = v.cliente.nombre if v.cliente else "Cliente General"
        writer.writerow([v.id, cliente_nombre, v.fecha.strftime("%d/%m/%Y %H:%M"), f"${v.total:,.0f}"]) 
    return response 


# 5. Configuración del Admin de Venta (Inlines, cálculo de total y filtro de fechas)[cite: 1]
@admin.register(Venta) 
class VentaAdmin(admin.ModelAdmin): 
    date_hierarchy = "fecha"  # Navegación y reporte rápido por rango de fechas[cite: 1]
    list_display = ("id", "cliente", "fecha", "total_display") 
    list_filter = ("fecha",)   # Filtro por rango de fechas (Caso 2)[cite: 1]
    search_fields = ("cliente__nombre", "id") 
    inlines = [DetalleVentaInline] # Inline de detalle de venta (Caso 2)[cite: 1]
    actions = [exportar_ventas_csv]

    @admin.display(description="Total ($)", ordering="id") 
    def total_display(self, obj): 
        # Cálculo del total de la venta (Caso 2)[cite: 1]
        return f"${obj.total:,.0f}"

    def get_queryset(self, request): 
        return super().get_queryset(request).select_related('cliente')

    def save_formset(self, request, form, formset, change):
        stock_anterior = {
            detalle.producto_id: detalle.cantidad
            for detalle in form.instance.detalles.all()
        } if change else {}
        with transaction.atomic():
            super().save_formset(request, form, formset, change)
            actualizar_stock_venta(form.instance, stock_anterior)

    def delete_model(self, request, obj):
        with transaction.atomic():
            devolver_stock_venta(obj)
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            for venta in queryset.prefetch_related('detalles'):
                devolver_stock_venta(venta)
            super().delete_queryset(request, queryset)


@admin.register(Producto) 
class ProductoAdmin(admin.ModelAdmin): 
    list_display = ("nombre", "sku", "precio", "stock", "activo") 
    search_fields = ("nombre", "sku") 
    list_filter = ("activo",) 
    ordering = ("nombre",) 


@admin.register(Cliente) 
class ClienteAdmin(admin.ModelAdmin): 
    list_display = ("nombre", "email") 
    search_fields = ("nombre", "email")
