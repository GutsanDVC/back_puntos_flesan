# 📊 Módulo Datawarehouse - Solo Lectura

## 📋 Descripción General

El módulo de datawarehouse está diseñado **exclusivamente para lectura de información** desde fuentes externas de datos. Utiliza la configuración existente `DATABASE_URL_DW` y proporciona métodos flexibles para realizar consultas variadas especificando esquema, tabla y query personalizada.

## 🎯 Características Principales

### ✅ **Solo Lectura**
- Conexiones de solo lectura al datawarehouse
- Sin operaciones de escritura (INSERT, UPDATE, DELETE)
- Consultas seguras y controladas
- Validaciones de seguridad contra SQL injection

### 🔧 **Métodos Flexibles**
- Especificar esquema dinámicamente
- Seleccionar tabla específica
- Ejecutar queries personalizadas
- Parámetros variables para consultas
- Límites automáticos de resultados (máximo 1000)

### 📊 **Consultas Variadas**
- Consultas simples por tabla
- Joins complejos entre tablas
- Filtros y agregaciones
- Paginación de resultados

## 🏗️ Arquitectura Implementada

```
app/
├── infrastructure/
│   └── datawarehouse/
│       ├── __init__.py
│       ├── client.py              # Cliente principal de lectura
│       ├── connection.py          # Gestión de conexiones
│       ├── query_builder.py       # Constructor y validador de queries
│       └── exceptions.py          # Excepciones específicas
├── application/
│   └── datawarehouse/
│       └── services/
│           └── datawarehouse_service.py  # Servicio de consultas
└── interfaces/
    └── api/
        └── routers/
            └── datawarehouse.py   # Endpoints REST
```

## 🔌 Métodos Principales

### 1. **Consulta por Esquema y Tabla**
```python
await datawarehouse_service.query_table(
    schema="hr",
    table="employees",
    columns=["id", "name", "email"],
    filters={"is_active": True},
    limit=100,
    offset=0
)
```

### 2. **Query Personalizada**
```python
await datawarehouse_service.execute_custom_query(
    query="SELECT * FROM hr.employees WHERE department_id = :dept_id",
    parameters={"dept_id": 5}
)
```

### 3. **Información de Esquemas y Tablas**
```python
# Obtener esquemas
schemas = await datawarehouse_service.get_available_schemas()

# Obtener tablas de un esquema
tables = await datawarehouse_service.get_schema_tables("hr")

# Obtener estructura de tabla
structure = await datawarehouse_service.get_table_structure("hr", "employees")
```

## 🛡️ Seguridad y Validaciones

### Validaciones Automáticas
- ✅ Solo queries SELECT permitidas
- ✅ Validación contra SQL injection
- ✅ Nombres de esquema/tabla validados
- ✅ Límite máximo de 1000 resultados
- ✅ Timeout de 60 segundos por query
- ✅ Conexiones de solo lectura

### Patrones Bloqueados
- ❌ INSERT, UPDATE, DELETE, DROP
- ❌ Comentarios SQL sospechosos
- ❌ UNION injection
- ❌ Nombres con caracteres especiales

## 🚀 Endpoints REST Disponibles

### **GET** `/api/v1/datawarehouse/test-connection`
Prueba la conexión al datawarehouse

### **GET** `/api/v1/datawarehouse/schemas`
Obtiene lista de esquemas disponibles

### **GET** `/api/v1/datawarehouse/schemas/{schema}/tables`
Obtiene tablas de un esquema específico

### **GET** `/api/v1/datawarehouse/schemas/{schema}/tables/{table}`
Obtiene estructura completa de una tabla

### **POST** `/api/v1/datawarehouse/query/custom`
Ejecuta una query personalizada
```json
{
  "query": "SELECT * FROM schema.table WHERE column = :param",
  "parameters": {"param": "value"}
}
```

### **POST** `/api/v1/datawarehouse/query/table`
Consulta una tabla específica
```json
{
  "schema": "hr",
  "table": "employees",
  "columns": ["id", "name", "email"],
  "filters": {"is_active": true},
  "order_by": "name",
  "limit": 50,
  "offset": 0
}
```

## ⚙️ Configuración

### Usa Configuración Existente
El módulo utiliza la configuración ya existente:
- `DATABASE_URL_DW`: URL de conexión al datawarehouse
- No requiere configuración adicional

### Configuraciones por Defecto
- **Timeout de conexión:** 30 segundos
- **Timeout de query:** 60 segundos  
- **Máximo resultados:** 1000 filas
- **Modo:** Solo lectura

## 🧪 Pruebas

### Ejecutar Script de Prueba
```bash
pipenv run python test_datawarehouse.py
```

### Pruebas Incluidas
1. ✅ Test de conexión
2. ✅ Obtener esquemas disponibles
3. ✅ Listar tablas de un esquema
4. ✅ Obtener estructura de tabla
5. ✅ Query simple a tabla
6. ✅ Query personalizada

## 🔐 Seguridad

### Autenticación
- **Todos los endpoints requieren rol ADMIN**
- Usar token de autenticación válido
- En desarrollo: usuario mock automático

### Permisos Necesarios
```python
# Solo usuarios ADMIN pueden acceder
current_user: CurrentUser = Depends(require_admin)
```

## 📝 Ejemplos de Uso

### Desde Python
```python
from app.application.datawarehouse.services.datawarehouse_service import datawarehouse_service

# Test de conexión
result = await datawarehouse_service.test_connection()

# Query simple
data = await datawarehouse_service.query_table(
    schema="public",
    table="users",
    limit=10
)

# Query personalizada
custom_data = await datawarehouse_service.execute_custom_query(
    "SELECT COUNT(*) as total FROM public.users"
)
```

### Desde API REST
```bash
# Test de conexión
curl -X GET "http://localhost:8001/api/v1/datawarehouse/test-connection" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Query personalizada
curl -X POST "http://localhost:8001/api/v1/datawarehouse/query/custom" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "SELECT * FROM public.users LIMIT 5"}'
```

## 🚨 Limitaciones Actuales

- ✅ Solo lectura (sin escritura)
- ✅ Máximo 1000 resultados por query
- ✅ Timeout de 60 segundos
- ✅ Solo usuarios ADMIN
- ✅ Una conexión por request

## 🔄 Próximas Mejoras

- [ ] Cache de resultados frecuentes
- [ ] Métricas de performance
- [ ] Logs de auditoría
- [ ] Queries favoritas
- [ ] Export a CSV/Excel

## ✅ Estado del Módulo

**🎉 COMPLETAMENTE FUNCIONAL**

El módulo de datawarehouse está listo para usar con:
- ✅ Conexión segura de solo lectura
- ✅ Validaciones de seguridad completas
- ✅ Endpoints REST documentados
- ✅ Manejo robusto de errores
- ✅ Script de pruebas incluido

**¡Listo para consultar datos del datawarehouse de forma segura!**
