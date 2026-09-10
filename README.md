# Backend — Psicóloga Alejandra

API construida con FastAPI y SQLAlchemy. Incluye el endpoint de contacto que consume el frontend y una base preparada para autenticación, usuarios y administración.

Los datos locales se guardan en `data/alejandra.db` usando SQLite. Ese archivo no se versiona. El endpoint `GET /api/content` devuelve el contenido configurable de la página; mientras no haya contenido guardado, responde `{}` y el frontend conserva sus textos de respaldo.

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

Inicia la API en `http://localhost:8080` y PostgreSQL para el entorno local.

## Próximos pasos de administración

- Migraciones con Alembic antes de desplegar en producción.
- Modelo de usuarios y autenticación con roles.
- Panel de administración protegido para gestionar consultas y citas.
