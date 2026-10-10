import csv

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse

from .models import Cliente, DetalleVenta, Producto, Venta
from .stock import actualizar_stock_venta, devolver_stock_venta


admin.site.site_header = "Control de Ventas - Tienda"
admin.site.site_title = "Admin Ventas"
admin.site.index_title = "Gestión de Productos y Registro de Ventas"


class DetalleVentaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            producto = form.cleaned_data.get("producto")
            cantidad = form.cleaned_data.get("cantidad")
            if producto and cantidad:
                disponible = producto.stock
                if form.instance.pk and form.instance.producto_id == producto.id:
                    disponible += form.instance.cantidad
                if cantidad > disponible:
                    raise ValidationError(
                        f"Stock insuficiente para {producto.nombre}. Disponible: {disponible}."
                    )


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    formset = DetalleVentaInlineFormSet
    fields = ("producto", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)


@admin.action(description="Exportar ventas seleccionadas a CSV")
def exportar_ventas_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reporte_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID Venta", "Cliente", "Fecha", "Total"])
    for venta in queryset.select_related("cliente").prefetch_related("detalles__producto"):
        cliente = venta.cliente.nombre if venta.cliente else "Cliente General"
        writer.writerow(
            [venta.id, cliente, venta.fecha.strftime("%d/%m/%Y %H:%M"), f"${venta.total:,.0f}"]
        )
    return response


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    date_hierarchy = "fecha"
    list_display = ("id", "cliente", "fecha", "total_display")
    list_filter = ("fecha",)
    search_fields = ("cliente__nombre", "id")
    inlines = [DetalleVentaInline]
    actions = [exportar_ventas_csv]

    @admin.display(description="Total ($)", ordering="id")
    def total_display(self, obj):
        return f"${obj.total:,.0f}"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("cliente")

    def save_formset(self, request, form, formset, change):
        stock_anterior = (
            {
                detalle.producto_id: detalle.cantidad
                for detalle in form.instance.detalles.all()
            }
            if change
            else {}
        )
        with transaction.atomic():
            super().save_formset(request, form, formset, change)
            actualizar_stock_venta(form.instance, stock_anterior)

    def delete_model(self, request, obj):
        with transaction.atomic():
            devolver_stock_venta(obj)
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            for venta in queryset.prefetch_related("detalles"):
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
