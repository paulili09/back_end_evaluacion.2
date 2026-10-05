from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Venta

def lista_ventas(request):
    ventas_list = Venta.objects.all().order_by('-fecha')
    paginator = Paginator(ventas_list, 5)  # Paginación de 5 en 5[cite: 1]
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ventas/lista_ventas.html', {'page_obj': page_obj})

def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta.delete()
        messages.success(request, f"La venta #{pk} fue eliminada correctamente.")  # Mensaje de feedback[cite: 1]
        return redirect('lista_ventas')
    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})
