from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),
]