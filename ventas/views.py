from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Venta
from .forms import VentaForm, DetalleVentaFormSet

def lista_ventas(request):
    ventas_list = Venta.objects.all().order_by('-fecha')
    
    # Paginación (5 ventas por página para la rúbrica)
    paginator = Paginator(ventas_list, 5)
    page_number = request.GET.get('page')
    ventas = paginator.get_page(page_number)
    
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})

def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            venta = form.save()
            
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.venta = venta
                if not detalle.precio_unitario and detalle.producto:
                    detalle.precio_unitario = detalle.producto.precio
                detalle.save()

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
    venta.delete()
    messages.success(request, f"Venta #{pk} eliminada correctamente.")
    return redirect('lista_ventas')