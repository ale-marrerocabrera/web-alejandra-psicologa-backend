# Backend — Psicóloga Alejandra

API construida con FastAPI y SQLAlchemy. Incluye el endpoint de contacto que consume el frontend y una base preparada para autenticación, usuarios y administración.

Los datos locales se guardan en `data/alejandra.db` usando SQLite. Ese archivo no se versiona. En cambio, `data/homepage-content.json` sí se versiona: sirve de semilla y se carga al crear una base nueva. El endpoint `GET /api/content` devuelve el contenido configurable de la página.

Con `APP_ENV=development`, el contenido se vuelve a sincronizar desde ese JSON en cada inicio de la API. En producción se conserva el contenido ya guardado para no sobrescribir ediciones del panel de administración.

Las tablas se gestionan con Alembic. Cuando cambie un modelo, se crea y revisa una nueva migración antes de desplegarla:

```bash
alembic revision --autogenerate -m "describe el cambio"
alembic upgrade head
```

## Administradora

Al iniciar una base nueva, configura una única cuenta administradora mediante variables de entorno; nunca se guardan en el repositorio:

```bash
export ADMIN_EMAIL="tu-email@ejemplo.com"
export ADMIN_PASSWORD="una-contraseña-larga-y-única"
```

La API crea esa cuenta solo si todavía no existe una administradora. La contraseña se almacena con Argon2. Las sesiones se guardan en base de datos y se entregan con una cookie `HttpOnly`; las operaciones de escritura privadas requieren además un token CSRF.

En producción configura `SESSION_COOKIE_SECURE=true` y sirve frontend y API exclusivamente mediante HTTPS.

## API privada de administración

Todas las rutas bajo `/api/admin/` requieren una sesión de administradora. Las rutas de escritura requieren además el encabezado `X-CSRF-Token`, con el mismo valor que la cookie `admin_csrf`:

- `GET` y `PUT /api/admin/content/homepage`: consultar y actualizar el contenido de la página.
- `POST /api/admin/uploads`: subir imágenes JPG, PNG o WEBP de hasta 5 MB.
- `GET /api/admin/messages`: listar mensajes, con filtros por estado y paginación.
- `PATCH /api/admin/messages/{id}`: marcar un mensaje como `unread`, `read` o `archived`.
- `DELETE /api/admin/messages/{id}`: eliminar un mensaje.

El contenido de inicio se valida con el mismo contrato en tres puntos: al cargar la semilla, al responder la ruta pública y antes de guardar una edición privada. Si falta una sección, un texto obligatorio o se añaden campos no reconocidos, la API rechaza la edición con `422` y conserva la versión anterior.

Las imágenes subidas se sirven desde `/api/uploads/` y se guardan en `data/uploads` por defecto. Docker Compose configura el directorio `/app/data/uploads` en el volumen persistente `uploads_data`, por lo que las imágenes permanecen tras reiniciar o recrear el contenedor.

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en `http://localhost:8080/docs`.

## Docker

```bash
docker compose up --build
```

En producción, antes de iniciar, copia `.env.production.example` a `.env` en
el servidor y reemplaza todos sus valores. Ese archivo no se versiona. La API
solo queda disponible en `127.0.0.1:18080`; el Nginx del servidor debe
publicar `https://tudominio.es/api/` y reenviar las solicitudes a ese puerto.
También debe enviar los encabezados `Host`, `X-Forwarded-For` y
`X-Forwarded-Proto`.

La configuración de producción aplica las migraciones pendientes antes de
arrancar, conserva el contenido guardado en la base de datos y usa cookies de
sesión seguras exclusivamente por HTTPS.

## Próximos pasos de administración

- Migraciones con Alembic antes de desplegar en producción.
- Modelo de usuarios y autenticación con roles.
- Panel de administración protegido para gestionar consultas y citas.
