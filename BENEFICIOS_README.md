# 🎁 CRUD de Beneficios - Documentación Completa

## 📋 Descripción

Este módulo implementa un CRUD completo para la gestión de beneficios siguiendo los principios de **Arquitectura Limpia**. Los beneficios representan ventajas o recompensas que pueden obtener los usuarios del sistema.

## 🏗️ Estructura del Proyecto

```
app/
├── domain/
│   └── beneficios/
│       ├── entities/
│       │   └── beneficio.py          # Entidad de dominio pura
│       └── services/
│           └── beneficio_service.py  # Servicios de dominio
├── application/
│   └── beneficios/
│       ├── commands.py               # Comandos (escritura)
│       ├── queries.py                # Queries (lectura)
│       ├── dto.py                    # Data Transfer Objects
│       └── ports.py                  # Interfaces/Puertos
├── infrastructure/
│   └── db/
│       ├── models/
│       │   └── beneficio_model.py    # Modelo SQLAlchemy
│       └── repositories/
│           └── beneficio_repository.py # Implementación del repositorio
└── interfaces/
    └── api/
        ├── routers/
        │   └── beneficios.py         # Endpoints REST
        └── schemas/
            └── beneficio_schemas.py  # Esquemas Pydantic
```

## 📊 Modelo de Datos

### Campos del Beneficio

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | UUID | Identificador único | `123e4567-e89b-12d3-a456-426614174000` |
| `imagen` | String(500) | URL o ruta de la imagen | `host/media/beneficios/CambiodeCasa.png` |
| `beneficio` | String(200) | Nombre del beneficio | `Día Cambio de Casa` |
| `detalle` | Text | Descripción detallada | `Un día libre para tu cambio de casa` |
| `regla1` | String(200) | Primera regla | `1 Vez por año` |
| `regla2` | String(200) | Segunda regla | `1 Vez por mes` |
| `valor` | Integer | Valor en puntos | `350` |
| `is_active` | Boolean | Estado activo | `true` |
| `created_at` | DateTime | Fecha de creación | `2023-01-01T00:00:00Z` |
| `updated_at` | DateTime | Fecha de actualización | `2023-01-02T00:00:00Z` |

## 🚀 Endpoints de la API

### Base URL: `/api/v1/beneficios`

#### 📝 Crear Beneficio
```http
POST /api/v1/beneficios
Authorization: Bearer {token}
Content-Type: application/json

{
  "imagen": "host/media/beneficios/CambiodeCasa.png",
  "beneficio": "Día Cambio de Casa",
  "detalle": "Un día libre para tu cambio de casa",
  "regla1": "1 Vez por año",
  "regla2": "1 Vez por mes",
  "valor": 350
}
```

**Respuesta (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "imagen": "host/media/beneficios/CambiodeCasa.png",
  "beneficio": "Día Cambio de Casa",
  "detalle": "Un día libre para tu cambio de casa",
  "regla1": "1 Vez por año",
  "regla2": "1 Vez por mes",
  "valor": 350,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": null
}
```

#### 📖 Obtener Beneficio por ID
```http
GET /api/v1/beneficios/{beneficio_id}
Authorization: Bearer {token}
```

#### 📋 Listar Beneficios
```http
GET /api/v1/beneficios?page=1&size=10&is_active=true
Authorization: Bearer {token}
```

**Parámetros de consulta:**
- `page` (int, opcional): Número de página (default: 1)
- `size` (int, opcional): Tamaño de página (default: 10, max: 100)
- `is_active` (bool, opcional): Filtrar por estado activo

#### 🔍 Buscar Beneficios
```http
GET /api/v1/beneficios/search/?q=cambio&page=1&size=10
Authorization: Bearer {token}
```

#### ✏️ Actualizar Beneficio
```http
PUT /api/v1/beneficios/{beneficio_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "beneficio": "Día Cambio de Casa Actualizado",
  "valor": 400
}
```

#### 🗑️ Desactivar Beneficio
```http
DELETE /api/v1/beneficios/{beneficio_id}
Authorization: Bearer {token}
```

#### 📊 Resumen de Beneficios
```http
GET /api/v1/beneficios/summary/
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "total_beneficios": 10,
  "beneficios_activos": 8,
  "valor_total": 2800
}
```

## 🔐 Permisos Requeridos

| Endpoint | Método | Permisos |
|----------|--------|----------|
| Crear | POST | Administrador |
| Obtener | GET | Usuario autenticado |
| Listar | GET | Usuario autenticado |
| Buscar | GET | Usuario autenticado |
| Actualizar | PUT | Manager o Administrador |
| Desactivar | DELETE | Administrador |
| Resumen | GET | Usuario autenticado |

## 🛠️ Instalación y Configuración

### 1. Ejecutar Migraciones

```bash
# Ejecutar script de migraciones
python run_migrations.py
```

### 2. Verificar Tablas Creadas

La migración creará:
- Tabla `beneficios` con todos los campos
- Índices para optimizar consultas
- Datos de ejemplo

### 3. Probar Endpoints

```bash
# Iniciar servidor
uvicorn main:app --reload

# Acceder a documentación interactiva
# http://localhost:8000/docs
```

## 📝 Ejemplos de Uso

### Crear un Beneficio con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/beneficios" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "imagen": "host/media/beneficios/DiaCumpleanos.png",
    "beneficio": "Día de Cumpleaños",
    "detalle": "Día libre por tu cumpleaños",
    "regla1": "1 Vez por año",
    "regla2": "Solo en tu cumpleaños",
    "valor": 200
  }'
```

### Listar Beneficios Activos

```bash
curl -X GET "http://localhost:8000/api/v1/beneficios?is_active=true&page=1&size=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Buscar Beneficios

```bash
curl -X GET "http://localhost:8000/api/v1/beneficios/search/?q=cumpleaños" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

### Casos de Prueba Sugeridos

1. **Validaciones de Dominio:**
   - Crear beneficio con nombre vacío (debe fallar)
   - Crear beneficio con valor negativo (debe fallar)
   - Crear beneficio con campos requeridos faltantes

2. **Reglas de Negocio:**
   - Crear beneficio con nombre duplicado (debe fallar)
   - Verificar unicidad de nombres
   - Validar cálculo de valor total

3. **Endpoints:**
   - Crear, leer, actualizar y desactivar beneficios
   - Paginación y filtros
   - Búsqueda por texto
   - Manejo de errores y códigos HTTP

## 🔧 Personalización

### Agregar Nuevos Campos

1. **Actualizar Entidad de Dominio:**
```python
# app/domain/beneficios/entities/beneficio.py
@dataclass
class Beneficio:
    # ... campos existentes ...
    nuevo_campo: str
```

2. **Actualizar Modelo de Base de Datos:**
```python
# app/infrastructure/db/models/beneficio_model.py
class BeneficioModel(Base):
    # ... campos existentes ...
    nuevo_campo: Mapped[str] = mapped_column(String(100))
```

3. **Crear Migración:**
```sql
-- migrations/002_add_nuevo_campo.sql
ALTER TABLE beneficios ADD COLUMN nuevo_campo VARCHAR(100);
```

4. **Actualizar Esquemas y DTOs**

### Agregar Nuevas Validaciones

```python
# app/domain/beneficios/services/beneficio_service.py
@staticmethod
def validate_custom_rule(beneficio: Beneficio) -> bool:
    # Implementar validación personalizada
    return True
```

## 📚 Arquitectura Limpia

Este módulo sigue los principios de **Arquitectura Limpia**:

- **Dominio:** Entidades y servicios puros, sin dependencias externas
- **Aplicación:** Casos de uso, comandos y queries
- **Infraestructura:** Implementaciones concretas (base de datos, etc.)
- **Interfaces:** API REST, esquemas de validación

### Beneficios de esta Arquitectura:

1. **Testabilidad:** Cada capa se puede probar independientemente
2. **Mantenibilidad:** Código organizado y fácil de modificar
3. **Escalabilidad:** Fácil agregar nuevas funcionalidades
4. **Flexibilidad:** Cambiar implementaciones sin afectar la lógica de negocio

## 🐛 Solución de Problemas

### Error: "Beneficio ya existe"
- **Causa:** Intentar crear un beneficio con nombre duplicado
- **Solución:** Usar un nombre único o actualizar el existente

### Error: "Valor no puede ser negativo"
- **Causa:** Validación de dominio
- **Solución:** Proporcionar un valor >= 0

### Error de Permisos
- **Causa:** Token inválido o permisos insuficientes
- **Solución:** Verificar autenticación y roles de usuario

## 📈 Métricas y Monitoreo

El sistema incluye logging automático para:
- Creación de beneficios
- Actualizaciones
- Errores de validación
- Consultas de búsqueda

## 🚀 Próximas Mejoras

- [ ] Historial de cambios en beneficios
- [ ] Categorías de beneficios
- [ ] Sistema de aprobación
- [ ] Notificaciones automáticas
- [ ] Reportes avanzados
- [ ] Cache para consultas frecuentes

---

**¡El CRUD de beneficios está listo para usar! 🎉**
