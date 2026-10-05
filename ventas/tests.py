from django.test import TestCase
from django.urls import reverse
from .models import Producto, Venta, DetalleVenta


class ProductoModelTest(TestCase):
    def test_crear_producto(self):
        """Verifica la creación correcta de un producto."""
        producto = Producto.objects.create(nombre="Teclado Mecánico", precio=25000)
        self.assertEqual(producto.nombre, "Teclado Mecánico")
        self.assertEqual(producto.precio, 25000)
        self.assertEqual(str(producto), "Teclado Mecánico ($25,000)")


class VentaModelTest(TestCase):
    def setUp(self):
        self.producto1 = Producto.objects.create(nombre="Mouse Gamer", precio=15000)
        self.producto2 = Producto.objects.create(nombre="Audífonos", precio=30000)
        self.venta = Venta.objects.create(cliente="Juan Pérez")

    def test_calculo_subtotal_y_total_venta(self):
        """Verifica que los subtotales y el total acumulado de la venta se calculen correctamente."""
        # Se agregan 2 Mouse Gamer ($15.000 c/u -> $30.000)
        DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto1,
            cantidad=2
        )
        # Se agrega 1 Audífono ($30.000 c/u -> $30.000)
        DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto2,
            cantidad=1
        )

        # Total esperado = $60.000
        self.assertEqual(self.venta.total(), 60000)

    def test_asignacion_automatica_precio_unitario(self):
        """Verifica que el precio unitario se asigne automáticamente desde el producto al guardar el detalle."""
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto1,
            cantidad=1
        )
        self.assertEqual(detalle.precio_unitario, 15000)


class VentaViewsTest(TestCase):
    def setUp(self):
        self.venta = Venta.objects.create(cliente="María López")

    def test_vista_lista_ventas_status_code(self):
        """Verifica que la página principal de lista de ventas responda con código 200."""
        response = self.client.get(reverse('lista_ventas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ventas/lista_ventas.html')

    def test_vista_eliminar_venta(self):
        """Verifica que una venta se elimine correctamente mediante la vista POST."""
        url = reverse('eliminar_venta', kwargs={'pk': self.venta.id})
        response = self.client.post(url)
        
        # Debe redirigir a la lista de ventas tras eliminar
        self.assertRedirects(response, reverse('lista_ventas'))
        # Comprobar que ya no existe en la BD
        self.assertFalse(Venta.objects.filter(id=self.venta.id).exists())
