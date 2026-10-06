from django import forms
from .models import Venta, DetalleVenta, Cliente, Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente']
        widgets = {
            'cliente': forms.Select(),
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(),
            'cantidad': forms.NumberInput(attrs={'min': 1, 'value': 1}),
            'precio_unitario': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El campo de precio unitario no es obligatorio en la interfaz
        self.fields['precio_unitario'].required = False

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        precio_unitario = cleaned_data.get('precio_unitario')

        # Si el usuario no ingresó un precio, se asigna automáticamente el del producto seleccionado
        if producto and not precio_unitario:
            cleaned_data['precio_unitario'] = producto.precio
            self.cleaned_data['precio_unitario'] = producto.precio
            
        return cleaned_data