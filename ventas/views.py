from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.core.paginator import Paginator
from datetime import datetime
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm, BaseDetalleVentaFormSet

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    formset=BaseDetalleVentaFormSet,
    extra=1,
    can_delete=True,
)

def lista_ventas(request):
    ventas = Venta.objects.select_related('cliente').all().order_by('-fecha')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    error = validar_rango_fechas(fecha_inicio, fecha_fin)
    if error:
        ventas = Venta.objects.none()
        messages.error(request, error)
    else:
        if fecha_inicio:
            ventas = ventas.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__date__lte=fecha_fin)

    paginator = Paginator(ventas, 10)
    pagina = paginator.get_page(request.GET.get('page'))
    return render(request, 'ventas/listas_ventas.html', {
        'ventas': pagina,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'error': error,
    })

def crear_venta(request):
    return guardar_venta(request)

def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return guardar_venta(request, venta)

def guardar_venta(request, venta=None):
    es_edicion = venta is not None
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save()
                formset.instance = venta
                formset.save()
            accion = 'actualizada' if es_edicion else 'registrada'
            messages.success(request, f'Venta #{venta.id} {accion} correctamente.')
            return redirect('lista_ventas')
        messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta)

    return render(request, 'ventas/crear_venta.html', {
        'form': form,
        'formset': formset,
        'venta': venta,
        'es_edicion': es_edicion,
    })


def validar_rango_fechas(fecha_inicio, fecha_fin):
    try:
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d') if fecha_inicio else None
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d') if fecha_fin else None
    except ValueError:
        return 'Usa fechas válidas con el formato AAAA-MM-DD.'
    if inicio and fin and inicio > fin:
        return 'La fecha inicial no puede ser posterior a la fecha final.'
    return ''

def reporte_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    error = validar_rango_fechas(fecha_inicio, fecha_fin)
    if not error:
        if fecha_inicio:
            ventas = ventas.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__date__lte=fecha_fin)
    else:
        ventas = Venta.objects.none()

    ventas = list(ventas.order_by('-fecha'))
    total = sum(venta.total for venta in ventas)
    return render(request, 'ventas/reporte_ventas.html', {
        'ventas': ventas,
        'total': total,
        'cantidad_ventas': len(ventas),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'error': error,
    })

def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta.delete()
        messages.success(request, f"Venta #{pk} eliminada correctamente.")
        return redirect('lista_ventas')
    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})
