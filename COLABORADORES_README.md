# 👥 Módulo Colaboradores - Consulta desde Datawarehouse

## 📋 Descripción General

El módulo de colaboradores permite consultar información de empleados desde la tabla `sap_maestro_colaborador` del esquema `flesan_rrhh` en el datawarehouse. Proporciona endpoints REST con filtros flexibles para obtener datos de colaboradores de forma segura y eficiente.

## 🎯 Características Principales

### ✅ **Consultas Flexibles**
- Filtros por múltiples campos
- Paginación automática
- Ordenamiento personalizable
- Búsqueda por nombre

### 🔍 **Filtros Disponibles**
- `empl_status` - Estado del empleado
- `user_id` - ID del usuario
- `national_id` - Cédula nacional
- `first_name` - Primer nombre
- `last_name` - Apellido paterno
- `correo_flesan` - Correo corporativo
- `centro_costo` - Centro de costo
- `external_cod_cargo` - Código externo del cargo
- `fecha_ingreso` - Fecha de ingreso
- `external_cod_tipo_contrato` - Código tipo de contrato
- `np_lider` - Nombre del líder

### 📊 **Campos Disponibles**
Basados en la tabla `sap_maestro_colaborador`:
- Información personal: nombres, apellidos, cédula, correos
- Información laboral: cargo, centro de costo, departamento, división
- Fechas: ingreso, término, antigüedad, nacimiento
- Estructura organizacional: líder, ubicación, tipo de contrato

## 🚀 Endpoints Disponibles

### **GET** `/api/v1/colaboradores/`
Lista colaboradores con filtros por query parameters

**Parámetros:**
```
?empl_status=A&centro_costo=CC001&limit=50&offset=0
```

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/colaboradores/?empl_status=A&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **POST** `/api/v1/colaboradores/query`
Consulta avanzada con filtros en el body

**Body:**
```json
{
  "filters": {
    "empl_status": "A",
    "centro_costo": "CC001",
    "np_lider": "Juan Pérez"
  },
  "columns": ["user_id", "first_name", "last_name", "correo_flesan"],
  "order_by": "first_name",
  "limit": 50,
  "offset": 0
}
```

### **GET** `/api/v1/colaboradores/user/{user_id}`
Obtiene un colaborador específico por user_id

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/colaboradores/user/12345" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **GET** `/api/v1/colaboradores/national-id/{national_id}`
Obtiene un colaborador específico por cédula nacional

### **GET** `/api/v1/colaboradores/activos`
Lista solo colaboradores con estado activo

### **GET** `/api/v1/colaboradores/centro-costo/{centro_costo}`
Lista colaboradores por centro de costo específico

### **GET** `/api/v1/colaboradores/lider/{np_lider}`
Lista colaboradores por líder específico

### **POST** `/api/v1/colaboradores/search`
Búsqueda por nombre (first_name, last_name, second_last_name)

**Body:**
```json
{
  "search_term": "Juan",
  "limit": 20,
  "offset": 0
}
```

### **GET** `/api/v1/colaboradores/info`
Información de la tabla (total registros, campos disponibles, etc.)

## 📝 Ejemplos de Uso

### 1. **Listar Colaboradores Activos**
```bash
curl -X GET "http://localhost:8000/api/v1/colaboradores/activos?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. **Filtrar por Centro de Costo**
```bash
curl -X GET "http://localhost:8000/api/v1/colaboradores/?centro_costo=CC001&empl_status=A" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. **Buscar por Nombre**
```bash
curl -X POST "http://localhost:8000/api/v1/colaboradores/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"search_term": "María", "limit": 5}'
```

### 4. **Consulta Avanzada con Filtros Múltiples**
```bash
curl -X POST "http://localhost:8000/api/v1/colaboradores/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "filters": {
      "empl_status": "A",
      "centro_costo": "CC001",
      "external_cod_tipo_contrato": "INDEFINIDO"
    },
    "columns": ["user_id", "first_name", "last_name", "correo_flesan", "fecha_ingreso"],
    "order_by": "fecha_ingreso",
    "limit": 25
  }'
```

### 5. **Obtener Colaborador Específico**
```bash
curl -X GET "http://localhost:8000/api/v1/colaboradores/user/12345" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Arquitectura Implementada

```
app/
├── application/
│   └── datawarehouse/
│       ├── services/
│       │   └── colaboradores_service.py    # Lógica de negocio
│       └── dto/
│           └── colaboradores_dto.py        # DTOs para requests/responses
└── interfaces/
    └── api/
        └── routers/
            └── colaboradores.py            # Endpoints REST
```

## 🛡️ Seguridad

### **Autenticación Requerida**
- Todos los endpoints requieren **rol ADMIN**
- Token de autenticación válido obligatorio
- En desarrollo: usuario mock automático disponible

### **Validaciones**
- Filtros validados contra campos permitidos
- Límites de resultados (máximo 1000)
- Parámetros sanitizados contra SQL injection
- Solo queries SELECT permitidas

## 🧪 Testing

### **Ejecutar Pruebas**
```bash
pipenv run python test_colaboradores.py
```

### **Pruebas Incluidas**
1. ✅ Información de la tabla
2. ✅ Consulta básica
3. ✅ Filtro por colaboradores activos
4. ✅ Búsqueda por nombre
5. ✅ Filtros específicos
6. ✅ Consulta por user_id

## 📊 Respuestas de la API

### **Respuesta Estándar de Lista**
```json
{
  "data": [
    {
      "user_id": 12345,
      "empl_status": "A",
      "first_name": "Juan",
      "last_name": "Pérez",
      "second_last_name": "González",
      "national_id": "12345678-9",
      "correo_flesan": "juan.perez@flesan.com",
      "centro_costo": "CC001",
      "nombre_centro_costo": "Administración",
      "departamento": "RRHH",
      "nombre_departamento": "Recursos Humanos",
      "np_lider": "María Silva",
      "fecha_ingreso": "2020-01-15",
      "external_cod_cargo": "ANALISTA",
      "external_cod_tipo_contrato": "INDEFINIDO"
    }
  ],
  "total_records": 1,
  "limit": 100,
  "offset": 0,
  "filters_applied": {
    "empl_status": "A"
  }
}
```

### **Respuesta de Información de Tabla**
```json
{
  "schema": "flesan_rrhh",
  "table": "sap_maestro_colaborador",
  "total_records": 1500,
  "columns": 45,
  "filterable_fields": [
    "centro_costo",
    "correo_flesan",
    "empl_status",
    "external_cod_cargo",
    "external_cod_tipo_contrato",
    "fecha_ingreso",
    "first_name",
    "last_name",
    "national_id",
    "np_lider",
    "user_id"
  ],
  "default_columns": ["user_id", "empl_status", "first_name", "..."]
}
```

## ⚙️ Configuración

### **Usa Configuración Existente**
- Utiliza el módulo de datawarehouse existente
- Configuración `DATABASE_URL_DW` del archivo `.env`
- No requiere configuración adicional

### **Límites por Defecto**
- **Límite por consulta:** 100 registros (máximo 1000)
- **Timeout:** 60 segundos
- **Offset:** 0 por defecto

## 🚨 Limitaciones

- ✅ Solo lectura (sin modificaciones)
- ✅ Requiere rol ADMIN
- ✅ Máximo 1000 resultados por consulta
- ✅ Filtros limitados a campos específicos
- ✅ Dependiente de conectividad al datawarehouse

## 🔄 Casos de Uso Comunes

### **1. Dashboard de RRHH**
```javascript
// Obtener colaboradores activos por departamento
const activos = await fetch('/api/v1/colaboradores/activos?limit=100');
```

### **2. Búsqueda de Empleados**
```javascript
// Buscar empleado por nombre
const busqueda = await fetch('/api/v1/colaboradores/search', {
  method: 'POST',
  body: JSON.stringify({ search_term: 'María', limit: 10 })
});
```

### **3. Reportes por Centro de Costo**
```javascript
// Colaboradores por centro de costo
const porCentro = await fetch('/api/v1/colaboradores/centro-costo/CC001');
```

### **4. Validación de Usuario**
```javascript
// Verificar si usuario existe
const usuario = await fetch('/api/v1/colaboradores/user/12345');
```

## ✅ Estado del Módulo

**🎉 COMPLETAMENTE FUNCIONAL**

El módulo de colaboradores está listo para usar con:
- ✅ 9 endpoints REST documentados
- ✅ 11 filtros disponibles
- ✅ Validaciones de seguridad completas
- ✅ Paginación y ordenamiento
- ✅ Búsqueda flexible por nombre
- ✅ Script de pruebas incluido
- ✅ Documentación completa

**¡Listo para consultar datos de colaboradores desde el datawarehouse!** 🎯
