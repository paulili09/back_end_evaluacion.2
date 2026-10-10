from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Cliente, DetalleVenta, Producto, Venta


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]
        widgets = {"cliente": forms.Select()}


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad", "precio_unitario"]
        widgets = {
            "producto": forms.Select(),
            "cantidad": forms.NumberInput(attrs={"min": 1, "value": 1}),
            "precio_unitario": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["precio_unitario"].required = False

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")
        precio_unitario = cleaned_data.get("precio_unitario")

        if producto and not producto.activo:
            self.add_error("producto", "El producto seleccionado no está activo.")

        if producto and cantidad and cantidad > producto.stock:
            disponible = producto.stock
            if self.instance.pk and self.instance.producto_id == producto.id:
                disponible += self.instance.cantidad
            if cantidad > disponible:
                self.add_error(
                    "cantidad", f"Stock insuficiente. Disponible: {disponible}."
                )

        if producto and not precio_unitario:
            cleaned_data["precio_unitario"] = producto.precio
        return cleaned_data


class BaseDetalleVentaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        productos = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            producto = form.cleaned_data.get("producto")
            if producto in productos:
                raise ValidationError("No puedes repetir un producto en la misma venta.")
            if producto:
                productos.append(producto)
