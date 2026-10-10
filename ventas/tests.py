from django.test import TestCase
from django.urls import reverse
from .models import Cliente, Producto, Venta, DetalleVenta


class ProductoModelTest(TestCase):
    def test_crear_producto(self):
        """Verifica la creación correcta de un producto."""
        producto = Producto.objects.create(
            nombre="Teclado Mecánico", sku="TEC-001", precio=25000
        )
        self.assertEqual(producto.nombre, "Teclado Mecánico")
        self.assertEqual(producto.precio, 25000)
        self.assertEqual(str(producto), "Teclado Mecánico ($25,000)")


class VentaModelTest(TestCase):
    def setUp(self):
        self.producto1 = Producto.objects.create(
            nombre="Mouse Gamer", sku="MOU-001", precio=15000, stock=10
        )
        self.producto2 = Producto.objects.create(
            nombre="Audífonos", sku="AUD-001", precio=30000, stock=10
        )
        self.cliente = Cliente.objects.create(nombre="Juan Pérez")
        self.venta = Venta.objects.create(cliente=self.cliente)

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
        self.assertEqual(self.venta.total, 60000)

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
        cliente = Cliente.objects.create(nombre="María López")
        self.venta = Venta.objects.create(cliente=cliente)
        self.producto = Producto.objects.create(
            nombre="Monitor", sku="MON-001", precio=100000, stock=5
        )

    def test_vista_lista_ventas_status_code(self):
        """Verifica que la página principal de lista de ventas responda con código 200."""
        response = self.client.get(reverse('lista_ventas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ventas/listas_ventas.html')

    def test_vista_eliminar_venta(self):
        """Verifica que una venta se elimine correctamente mediante la vista POST."""
        url = reverse('eliminar_venta', kwargs={'pk': self.venta.id})
        response = self.client.post(url)
        
        # Debe redirigir a la lista de ventas tras eliminar
        self.assertRedirects(response, reverse('lista_ventas'))
        # Comprobar que ya no existe en la BD
        self.assertFalse(Venta.objects.filter(id=self.venta.id).exists())

    def test_reporte_rechaza_rango_invertido(self):
        response = self.client.get(
            reverse('reporte_ventas'),
            {'fecha_inicio': '2026-10-10', 'fecha_fin': '2026-10-01'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'fecha inicial no puede ser posterior')

    def test_crear_venta_con_detalle(self):
        response = self.client.post(
            reverse('crear_venta'),
            {
                'cliente': self.venta.cliente_id,
                'detalles-TOTAL_FORMS': '1',
                'detalles-INITIAL_FORMS': '0',
                'detalles-MIN_NUM_FORMS': '0',
                'detalles-MAX_NUM_FORMS': '1000',
                'detalles-0-producto': self.producto.id,
                'detalles-0-cantidad': '2',
                'detalles-0-precio_unitario': '',
            },
        )

        self.assertRedirects(response, reverse('lista_ventas'))
        detalle = DetalleVenta.objects.get(venta__cliente=self.venta.cliente)
        self.assertEqual(detalle.cantidad, 2)
        self.assertEqual(detalle.precio_unitario, 100000)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

    def test_eliminar_venta_devuelve_stock(self):
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=2,
        )
        self.producto.stock -= detalle.cantidad
        self.producto.save(update_fields=['stock'])

        response = self.client.post(
            reverse('eliminar_venta', kwargs={'pk': self.venta.id})
        )

        self.assertRedirects(response, reverse('lista_ventas'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
