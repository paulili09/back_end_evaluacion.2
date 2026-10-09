from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('editar/<int:pk>/', views.editar_venta, name='editar_venta'),
    path('reporte/', views.reporte_ventas, name='reporte_ventas'),
    path('eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),
]