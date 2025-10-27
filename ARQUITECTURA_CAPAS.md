# Arquitectura por Capas (Layered Architecture)

## 📋 Descripción

El proyecto ha sido migrado de **Clean Architecture** a una **Arquitectura por Capas** más simple y directa, manteniendo la separación de responsabilidades pero reduciendo la complejidad.

## 📁 Estructura del Proyecto

```
app/
│
├── core/                     # Configuración global y utilidades
│   ├── config.py             # Variables de entorno (Settings)
│   ├── database.py           # Conexión a BD (AsyncSession)
│   ├── logger.py             # Log centralizado
│   ├── security.py           # Autenticación y seguridad
│   ├── exceptions.py         # Excepciones personalizadas
│   └── utils/                # Utilidades compartidas
│
├── api/                      # Capa de presentación (FastAPI)
│   ├── routers/              # Endpoints organizados por módulo
│   │   ├── user_router.py
│   │   ├── health_router.py
│   │   └── ...
│   └── schemas/              # Validación entrada/salida (Pydantic)
│       ├── user_schema.py
│       └── ...
│
├── services/                 # Capa de negocio / aplicación
│   ├── user_service.py
│   └── ...
│
├── repositories/             # Capa de acceso a datos
│   ├── user_repository.py   # SQL RAW con text() y execute()
│   └── ...
│
├── sql/                      # SQLs documentados (opcional)
│   ├── user_queries.sql
│   └── ...
│
└── main.py                   # Punto de entrada del servidor
```

## 🔄 Flujo de Datos

```
Request → Router → Service → Repository → Database
                       ↓
Response ← Schema ← Service ← Repository ← Database
```

### 1. **API Layer** (Routers + Schemas)
- **Responsabilidad**: Recibir requests HTTP, validar datos de entrada/salida
- **Tecnología**: FastAPI + Pydantic
- **Ejemplo**: `app/api/routers/user_router.py`

```python
@router.post("/", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service)
):
    user = await service.create_user(...)
    return UserResponse(**user)
```

### 2. **Service Layer** (Lógica de Negocio)
- **Responsabilidad**: Validaciones de negocio, orquestación de operaciones
- **Sin dependencias de framework**
- **Ejemplo**: `app/services/user_service.py`

```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create_user(self, email, first_name, ...):
        # Validaciones de negocio
        if not validate_email(email):
            raise ValidationError("Email inválido")
        
        # Verificar unicidad
        if await self.repository.exists_by_email(email):
            raise ConflictError("Email ya existe")
        
        # Crear usuario
        return await self.repository.create(...)
```

### 3. **Repository Layer** (Acceso a Datos)
- **Responsabilidad**: Interacción con base de datos usando **SQL RAW**
- **Sin ORM** - Solo `text()` y `execute()`
- **Ejemplo**: `app/repositories/user_repository.py`

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, email, first_name, ...):
        query = text("""
            INSERT INTO puntos_flesan.users (...)
            VALUES (...)
            RETURNING *
        """)
        result = await self.session.execute(query, {...})
        return self._row_to_dict(result.fetchone())
```

## ⚙️ Reglas de Implementación

### ✅ SQL RAW Obligatorio

**CORRECTO:**
```python
query = text("SELECT * FROM schema.table WHERE id = :id")
result = await session.execute(query, {"id": value})
```

**INCORRECTO (No usar):**
```python
stmt = select(Model).where(Model.id == value)  # ❌ ORM prohibido
```

### ✅ Inyección de Dependencias

```python
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)
```

### ✅ Manejo de Errores

```python
try:
    user = await service.create_user(...)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=...)
except ConflictError as e:
    raise HTTPException(status_code=409, detail=...)
```

## 📦 Módulos Implementados

### ✅ Users (Migrado)
- ✅ Router: `app/api/routers/user_router.py`
- ✅ Service: `app/services/user_service.py`
- ✅ Repository: `app/repositories/user_repository.py`
- ✅ Schemas: `app/api/schemas/user_schema.py`
- ✅ SQL: `app/sql/user_queries.sql`

### ⏳ Beneficios (Pendiente migración)
- Actualmente en: `app/interfaces/api/routers/beneficios.py`
- Usa ORM - Necesita migración a SQL RAW

### ⏳ Datawarehouse (Pendiente migración)
- Actualmente en: `app/interfaces/api/routers/datawarehouse.py`

### ⏳ Colaboradores (Pendiente migración)
- Actualmente en: `app/interfaces/api/routers/colaboradores.py`

## 🚀 Ventajas de esta Arquitectura

1. **Simplicidad**: Menos capas y abstracciones que Clean Architecture
2. **Claridad**: Flujo de datos directo y fácil de seguir
3. **Mantenibilidad**: Código organizado por responsabilidades
4. **Performance**: SQL RAW optimizado sin overhead del ORM
5. **Testabilidad**: Cada capa es independiente y testeable

## 🔧 Cómo Agregar un Nuevo Módulo

### 1. Crear Schema (Pydantic)
```python
# app/api/schemas/producto_schema.py
class ProductoCreateRequest(BaseModel):
    nombre: str
    precio: float
```

### 2. Crear Repository (SQL RAW)
```python
# app/repositories/producto_repository.py
class ProductoRepository:
    async def create(self, ...):
        query = text("INSERT INTO ...")
        ...
```

### 3. Crear Service (Lógica de Negocio)
```python
# app/services/producto_service.py
class ProductoService:
    async def create_producto(self, ...):
        # Validaciones
        # Llamadas al repository
        ...
```

### 4. Crear Router (Endpoints)
```python
# app/api/routers/producto_router.py
@router.post("/")
async def create_producto(
    request: ProductoCreateRequest,
    service: ProductoService = Depends(get_producto_service)
):
    ...
```

### 5. Registrar en main.py
```python
from app.api.routers import producto_router
app.include_router(producto_router, prefix=settings.API_V1_PREFIX)
```

## 📝 Notas Importantes

- **No usar ORM**: Toda interacción con BD debe ser SQL RAW
- **Schemas vs Dicts**: Los services retornan dicts, los routers los convierten a Pydantic
- **Validaciones**: Negocio en Service, formato en Schema
- **Transacciones**: Manejadas automáticamente por `get_db()`
- **Logging**: Usar logger de `app.core.logger`

## 🔄 Migración desde Clean Architecture

La migración consolida:
- `domain/entities` + `domain/services` → `services/`
- `application/commands` + `application/queries` → `services/`
- `application/dto` → `api/schemas/`
- `infrastructure/repositories` → `repositories/`
- `interfaces/api/routers` → `api/routers/`

Ventaja: **Menos archivos, misma funcionalidad**
