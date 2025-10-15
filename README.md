# FastAPI Backend Template

Template de backend basado en **Arquitectura Limpia** con **FastAPI**, **SQLAlchemy 2.x**, **PostgreSQL**, **JWT** con cookies **HttpOnly**, y **pytest** para pruebas unitarias.

## 🏗️ Arquitectura

Este template sigue los principios de Arquitectura Limpia:

- **Separación de responsabilidades** por capas
- **Inyección de dependencias** explícita
- **Entidades de dominio puras** (sin ORM)
- **Seguridad, trazabilidad y testabilidad** integradas
- **DTOs** para entrada/salida, no modelos ORM

### Estructura del Proyecto

```
app/
├── core/                   # Configuración y utilidades centrales
│   ├── config.py          # Configuración con pydantic-settings
│   ├── exceptions.py      # Excepciones personalizadas
│   ├── logger.py          # Configuración de logging JSON
│   ├── security.py        # Roles, permisos y decoradores
│   └── utils/             # Utilidades compartidas
│
├── domain/                 # Capa de dominio (reglas de negocio)
│   └── users/             # Contexto de usuarios
│       ├── entities/      # Entidades puras
│       └── services/      # Servicios de dominio
│
├── application/           # Capa de aplicación (casos de uso)
│   └── users/
│       ├── dto.py         # Data Transfer Objects
│       ├── commands.py    # Casos de uso de escritura
│       ├── queries.py     # Casos de uso de lectura
│       └── ports.py       # Interfaces (puertos)
│
├── infrastructure/        # Capa de infraestructura
│   ├── db/               # Base de datos
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── repositories/ # Implementaciones de repositorios
│   │   └── session.py    # Configuración de sesión
│   ├── auth/             # Autenticación y autorización
│   └── external/         # Servicios externos
│
├── interfaces/           # Capa de interfaces (API)
│   └── api/
│       ├── routers/      # Routers de FastAPI
│       ├── schemas/      # Esquemas Pydantic
│       └── dependencies.py # Dependencias de FastAPI
│
└── tests/                # Tests organizados por tipo
    ├── unit/             # Tests unitarios
    ├── integration/      # Tests de integración
    └── e2e/              # Tests end-to-end
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+
- Servidor Linux (Ubuntu) con Apache y Nginx

### Instalación Local

1. **Clonar y configurar entorno:**
```bash
git clone <repository-url>
cd fastapi-backend-template
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Ejecutar localmente (desarrollo):**
```bash
uvicorn main:app --reload
```

### Acceso a la API

- **API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/

## 🔐 Autenticación

El sistema utiliza **JWT con cookies HttpOnly** para autenticación:

- **Validación JWT** con claves públicas (JWKS)
- **Cookies seguras** (`HttpOnly`, `Secure`, `SameSite=Lax`)
- **Roles y permisos** definidos en `core/security.py`
- **Decoradores** `@requires("rol")` o dependencias con `Depends()`

### Roles Disponibles

- `ADMIN`: Acceso completo al sistema
- `MANAGER`: Gestión de usuarios y recursos
- `USER`: Acceso básico de usuario
- `VIEWER`: Solo lectura

## 🗄️ Base de Datos

- **ORM:** SQLAlchemy 2.x (modo async)
- **Migraciones:** Alembic
- **Sesión:** Configurada en `infrastructure/db/session.py`
- **Repositorios:** Implementan interfaces de `application.ports`

### Ejecutar Migraciones

```bash
# Generar migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head
```

## 🧪 Testing

El proyecto incluye tests completos organizados por tipo:

```bash
# Ejecutar todos los tests
pytest

# Tests unitarios solamente
pytest tests/unit/

# Tests con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/domain/test_user_entity.py -v
```

### Tipos de Tests

- **Unit:** Dominio y aplicación (lógica de negocio)
- **Integration:** Repositorios y endpoints
- **E2E:** Flujos completos con mocks de autenticación

## 📝 Logging y Monitoreo

- **Logs JSON** estructurados con `trace_id`, `user_id`, `path`, `latency`
- **Excepciones unificadas** con códigos `APP-ERR-###`
- **Health checks** para Kubernetes (`/health/`, `/health/ready`, `/health/live`)

## 🛠️ Desarrollo

### Linting y Formateo

```bash
# Formatear código
black .
ruff check . --fix

# Type checking
mypy .
```

### Agregar Nuevo Contexto

Para agregar un nuevo bounded context (ej: `products`):

1. Crear estructura en `domain/products/`
2. Implementar DTOs, commands y queries en `application/products/`
3. Crear repositorio en `infrastructure/db/repositories/`
4. Agregar router en `interfaces/api/routers/`
5. Registrar router en `main.py`

### Variables de Entorno

Todas las configuraciones están centralizadas en `app/core/config.py`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_JWKS_URL: str
    AUTH_AUDIENCE: str
    SECRET_KEY: str
    # ... más configuraciones
```

## 🚢 Despliegue en Servidor

### Arquitectura de Despliegue

```
Frontend → Apache :80/443 → ProxyPass → Nginx :8080 → Gunicorn → FastAPI → PostgreSQL
```

### Despliegue Automático

```bash
# 1. Clonar el proyecto en el servidor
git clone <repository-url> /var/www/fastapi_app
cd /var/www/fastapi_app

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con configuraciones reales

# 3. Ejecutar script de despliegue
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh tu-dominio.com
```

### Despliegue Manual

Si prefieres configurar paso a paso, consulta la [Guía Detallada de Despliegue](deploy/README.md) que incluye:

- Configuración manual de todos los servicios
- Troubleshooting común
- Optimización de rendimiento
- Configuración de HTTPS
- Monitoreo y logs

### Monitoreo y Logs

| Servicio | Comando para ver logs |
|----------|----------------------|
| FastAPI/Gunicorn | `journalctl -u fastapi_app -f` |
| Nginx | `tail -f /var/log/nginx/error.log` |
| Apache | `tail -f /var/log/apache2/fastapi_error.log` |

## 📚 Documentación Adicional

- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy 2.x:** https://docs.sqlalchemy.org/en/20/
- **Pydantic:** https://docs.pydantic.dev/
- **Pytest:** https://docs.pytest.org/

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.
