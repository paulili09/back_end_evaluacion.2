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
- API REST protegida con JWT y CORS configurable para clientes externos.

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
Para forzar SQLite en una máquina que ya tenga variables PostgreSQL configuradas,
usa `USE_SQLITE=True`.

## API REST

La API está disponible bajo `/api/` y requiere un token JWT para sus
operaciones. Obtén los tokens con:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"tu-clave\"}"
```

Usa el `access` recibido en las peticiones protegidas:

```bash
curl http://127.0.0.1:8000/api/productos/ ^
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

Endpoints disponibles:

- `/api/productos/`
- `/api/clientes/`
- `/api/ventas/`
- `/api/detalles-venta/`
- `/api/token/` y `/api/token/refresh/`

El cliente web de demostración está disponible en `/cliente-api/`. Permite
obtener un JWT y ejecutar el CRUD de productos, clientes y ventas desde el
navegador: listar, crear, editar y eliminar mediante `GET`, `POST`, `PUT` y
`DELETE`. Incluye productos, clientes, ventas y detalles de venta; el control
de stock de ventas se mantiene en el flujo tradicional y en Admin.

Para permitir un cliente web externo, define `CORS_ALLOWED_ORIGINS` en `.env`
como una lista separada por comas, por ejemplo:
`http://localhost:5173,https://tu-cliente.vercel.app`.
El servidor responde con `Access-Control-Allow-Origin` únicamente para esos
orígenes; no se usa `CORS_ALLOW_ALL_ORIGINS`.

## Verificación y despliegue

```bash
python manage.py check --deploy
python manage.py test
python manage.py makemigrations --check
python manage.py collectstatic --noinput
```

En Vercel configura `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` y las cinco variables de
PostgreSQL. No subas `.venv/`
ni `.env`; ambos quedan excluidos mediante `.gitignore` y `.vercelignore`.
Con `DEBUG=False` se activan HTTPS, HSTS, cookies seguras, protección
`nosniff` y una política de referencia restrictiva.
Revisa los logs de la función si falla una migración o la conexión a la base
de datos.

La entrada de Vercel está en `index.py` y la configuración de rutas
está en `vercel.json`. Después del despliegue, ejecuta las migraciones contra la
base de datos de producción usando las mismas variables de entorno y verifica
la URL pública, `/admin/`, los archivos estáticos y los logs de la función.

### Lista de evidencias para la evaluación

- Obtener `access` y `refresh` en `/api/token/`.
- Recibir `401` al consultar `/api/productos/` sin autenticación.
- Consultar y modificar productos con `Authorization: Bearer <access>`.
- Mostrar el origen autorizado en la respuesta CORS desde el cliente externo.
- Para comprobar CORS localmente, ejecuta:

```powershell
curl.exe -i -X OPTIONS http://127.0.0.1:8000/api/productos/ `
  -H "Origin: http://localhost:5173" `
  -H "Access-Control-Request-Method: GET"
```

La respuesta debe incluir `Access-Control-Allow-Origin: http://localhost:5173`.
- Demostrar crear, editar y eliminar un producto desde `/cliente-api/`.
- Mostrar el descuento y la devolución de stock desde el flujo de ventas.
- Registrar en el video la URL pública y las decisiones de seguridad.

La guía de presentación y las evidencias solicitadas están en
`PRESENTACION_CASO_2.md`.
