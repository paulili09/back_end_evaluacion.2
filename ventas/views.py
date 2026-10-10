from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BaseDetalleVentaFormSet, DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta
from .stock import actualizar_stock_venta, devolver_stock_venta


DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    formset=BaseDetalleVentaFormSet,
    extra=1,
    can_delete=True,
)


def lista_ventas(request):
    ventas = Venta.objects.select_related("cliente").order_by("-fecha")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    error = validar_rango_fechas(fecha_inicio, fecha_fin)
    if error:
        ventas = Venta.objects.none()
        messages.error(request, error)
    else:
        if fecha_inicio:
            ventas = ventas.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__date__lte=fecha_fin)

    pagina = Paginator(ventas, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "ventas/listas_ventas.html",
        {"ventas": pagina, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "error": error},
    )


def crear_venta(request):
    return guardar_venta(request)


def editar_venta(request, pk):
    return guardar_venta(request, get_object_or_404(Venta, pk=pk))


def guardar_venta(request, venta=None):
    es_edicion = venta is not None
    if request.method == "POST":
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    stock_anterior = {}
                    if venta:
                        stock_anterior = {
                            detalle.producto_id: detalle.cantidad
                            for detalle in venta.detalles.all()
                        }
                    venta = form.save()
                    formset.instance = venta
                    formset.save()
                    actualizar_stock_venta(venta, stock_anterior)
                accion = "actualizada" if es_edicion else "registrada"
                messages.success(request, f"Venta #{venta.id} {accion} correctamente.")
                return redirect("lista_ventas")
            except ValidationError as error:
                messages.error(request, error.messages[0])
        messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta)

    return render(
        request,
        "ventas/crear_venta.html",
        {"form": form, "formset": formset, "venta": venta, "es_edicion": es_edicion},
    )


def validar_rango_fechas(fecha_inicio, fecha_fin):
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d") if fecha_inicio else None
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d") if fecha_fin else None
    except ValueError:
        return "Usa fechas válidas con el formato AAAA-MM-DD."
    if inicio and fin and inicio > fin:
        return "La fecha inicial no puede ser posterior a la fecha final."
    return ""


def reporte_ventas(request):
    ventas = Venta.objects.select_related("cliente").prefetch_related("detalles")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    error = validar_rango_fechas(fecha_inicio, fecha_fin)
    if error:
        ventas = Venta.objects.none()
    else:
        if fecha_inicio:
            ventas = ventas.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__date__lte=fecha_fin)

    ventas = list(ventas.order_by("-fecha"))
    return render(
        request,
        "ventas/reporte_ventas.html",
        {
            "ventas": ventas,
            "total": sum(venta.total for venta in ventas),
            "cantidad_ventas": len(ventas),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "error": error,
        },
    )


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == "POST":
        with transaction.atomic():
            devolver_stock_venta(venta)
            venta.delete()
        messages.success(request, f"Venta #{pk} eliminada correctamente.")
        return redirect("lista_ventas")
    return render(request, "ventas/confirmar_eliminar.html", {"venta": venta})
