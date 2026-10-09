# Control de Ventas

Aplicación Django para registrar ventas, productos, clientes y detalles de venta.

## Funciones del Caso 2

- CRUD de ventas con productos y cantidades.
- Cálculo automático de subtotales y total.
- Validación de productos activos, stock y productos repetidos.
- Listado paginado con filtro por rango de fechas.
- Reporte básico por rango de fechas.
- Django Admin personalizado con inline de detalles, búsqueda, filtros y total.
- Mensajes de éxito y error para las operaciones.
- Archivos estáticos servidos con WhiteNoise en producción.

## Ejecución local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Con las variables PostgreSQL vacías se utiliza SQLite local. Para Supabase, completa las variables del archivo `.env`.

## Verificación y despliegue

```bash
python manage.py check --deploy
python manage.py test
python manage.py collectstatic --noinput
```

En Vercel configura `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y las cinco variables de PostgreSQL. Revisa los logs de la función si falla una migración o la conexión a la base de datos.

