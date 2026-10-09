from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse
import csv
from .models import Producto, Venta, DetalleVenta

admin.site.site_header = "Control de Ventas – Tienda"
admin.site.site_title = "Admin Ventas"
admin.site.index_title = "Gestión de Productos y Registro de Ventas"

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock')
    search_fields = ('nombre',)

class DetalleVentaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            prod = form.cleaned_data.get('producto')
            cant = form.cleaned_data.get('cantidad')
            if prod and cant and cant > prod.stock:
                raise ValidationError(f"Stock insuficiente para {prod.nombre}")

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    formset = DetalleVentaInlineFormSet
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ("subtotal",)

@admin.action(description="Exportar ventas seleccionadas a CSV (Reporte)")
def exportar_ventas_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID Venta", "Cliente", "Fecha", "Total"])
    for v in queryset:
        cliente_nombre = v.cliente if v.cliente else "Cliente General"
        writer.writerow([v.id, cliente_nombre, v.fecha.strftime("%d/%m/%Y %H:%M"), v.total])
    return response

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente', 'id')
    inlines = [DetalleVentaInline]
    actions = [exportar_ventas_csv]
