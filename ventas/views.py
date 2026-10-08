from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm

DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta, form=DetalleVentaForm, extra=1, can_delete=False
)

def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'ventas/listas_ventas.html', {'ventas': ventas})

def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            venta = form.save()  # Se guarda la venta (sin asignar venta.total)
            
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.venta = venta
                if not detalle.precio_unitario and detalle.producto:
                    detalle.precio_unitario = detalle.producto.precio
                detalle.save()
            
            # Se eliminó la línea "venta.total = total_calculado"
            # El total se calcula solo al consultar el modelo mediante @property

            messages.success(request, f"¡Venta #{venta.id} registrada con éxito!")
            return redirect('lista_ventas')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = VentaForm()
        formset = DetalleVentaFormSet()

    return render(request, 'ventas/crear_venta.html', {
        'form': form,
        'formset': formset
    })

def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta.delete()
        messages.success(request, f"Venta #{pk} eliminada correctamente.")
        return redirect('lista_ventas')
    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})
