# Caso 2: Aplicación de Control de Venta

## 1. Problema y objetivo

La tienda necesita registrar sus ventas, controlar el inventario y consultar
resultados sin depender de registros manuales. La aplicación centraliza
productos, clientes, ventas y detalles de venta en Django.

## 2. Funcionalidades implementadas

- CRUD completo de ventas.
- Registro de productos con SKU, precio, stock y estado activo.
- Registro de clientes con nombre y correo electrónico.
- Detalles de venta mediante inline en Django Admin.
- Cálculo automático de subtotal y total.
- Validación de productos activos, cantidades y stock disponible.
- Descuento de stock al registrar o editar una venta.
- Restitución de stock al eliminar una venta.
- Reporte por rango de fechas.
- Paginación del listado principal.
- Mensajes de éxito y error para cada operación.
- Exportación de ventas seleccionadas a CSV desde Admin.
- Branding de la aplicación y del espacio de Django Admin.

## 3. Demostración del flujo CRUD

1. Entrar a `/admin/` y crear un producto con precio y stock.
2. Crear un cliente desde el Admin.
3. Entrar a la aplicación y registrar una venta con uno o más productos.
4. Comprobar que el total se calcula automáticamente.
5. Comprobar que el stock disminuye según la cantidad vendida.
6. Editar la venta y verificar que el stock se ajusta.
7. Eliminar la venta y verificar que el stock se devuelve.
8. Consultar el reporte y filtrar por fecha inicial y final.
9. Exportar las ventas seleccionadas a CSV desde el Admin.

## 4. Resultados conseguidos

La solución permite llevar el control de ventas y existencias en un flujo
consistente. Las transacciones protegen los cambios de inventario y las
validaciones evitan cantidades inválidas, productos inactivos y ventas
superiores al stock disponible.

## 5. Evidencias para la evaluación

Para la presentación se deben mostrar capturas o una demostración de:

- Productos y clientes registrados en Admin.
- Inline de detalles dentro de una venta.
- Stock antes y después de registrar una venta.
- Mensaje de confirmación después de guardar.
- Listado paginado.
- Reporte filtrado por fechas.
- Acción de exportación CSV.
- Branding del Admin.
- URL pública y logs del despliegue.

## 6. Configuración técnica

- Django con SQLite para desarrollo local.
- PostgreSQL/Supabase mediante variables de entorno para producción.
- WhiteNoise para archivos estáticos.
- Variables de entorno para secreto, debug, hosts, CSRF y base de datos.
- Migraciones versionadas en `ventas/migrations/`.
- Entrada de Vercel preparada en `index.py`, usando la aplicación WSGI de `core/wsgi.py`.

## 7. Comandos de verificación

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py migrate
python manage.py test
python manage.py collectstatic --noinput
```
