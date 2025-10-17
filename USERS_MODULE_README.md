# 👥 Módulo de Usuarios - Sistema de Puntos Flesan

## 📋 Descripción General

El módulo de usuarios gestiona la autenticación, autorización y administración de usuarios en el sistema de puntos de Flesan. Implementa un sistema jerárquico de roles con permisos específicos para cada nivel.

## 🎭 Roles del Sistema

### 1. **USER** (Usuario Base)
- **Descripción**: Empleado básico del sistema
- **Permisos**:
  - `redeem_points`: Canjear puntos por beneficios
  - `view_own_points`: Ver sus puntos disponibles
  - `view_own_history`: Ver su historial de transacciones
  - `view_benefits`: Ver catálogo de beneficios disponibles

### 2. **USER_LEADER** (Líder de Equipo)
- **Descripción**: Líder de equipo con responsabilidades sobre otros usuarios
- **Permisos**: Todos los de USER +
  - `view_team_points`: Ver puntos de personas a cargo
  - `view_team_history`: Ver historial de personas a cargo

### 3. **MANAGER** (Gerente)
- **Descripción**: Gerente con capacidades de administración
- **Permisos**: Todos los de USER_LEADER +
  - `view_company_history`: Ver historial de canje de toda la empresa
  - `manage_benefits`: Modificar, agregar o eliminar beneficios
  - `give_extra_points`: Entregar puntos extras a colaboradores
  - `create_users`: Agregar nuevos usuarios al sistema

### 4. **ADMIN** (Administrador)
- **Descripción**: Administrador del sistema con acceso completo
- **Permisos**: Todos los anteriores +
  - `create_managers`: Crear nuevos managers
  - `system_config`: Configuración del sistema

## 🗄️ Estructura de Base de Datos

### Tabla: `puntos_flesan.users`

```sql
CREATE TABLE puntos_flesan.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NULL,                    -- ID del datawarehouse (pendiente)
    email VARCHAR(255) UNIQUE NOT NULL,      -- Email del usuario
    first_name VARCHAR(100) NOT NULL,        -- Nombre
    last_name VARCHAR(100) NOT NULL,         -- Apellido
    puntos_disponibles INTEGER DEFAULT 0,    -- Puntos disponibles para canjear
    rol VARCHAR(50) NOT NULL,                -- Rol único del usuario
    permisos TEXT NOT NULL,                  -- JSON array de permisos
    is_active BOOLEAN DEFAULT TRUE,          -- Usuario activo
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL
);
```

## 🔐 Sistema de Autenticación

### Modo Desarrollo
- Usuario mock automático con rol ADMIN
- Bypass de autenticación para testing
- Solo activo cuando `ENVIRONMENT=development`

### Modo Producción
- Autenticación JWT con tokens
- Validación de tokens con JWKS
- Extracción de roles y permisos del token

## 🛡️ Dependencies de Autorización

### Básicas
```python
require_admin()                    # Solo ADMIN
require_manager_or_admin()         # MANAGER o ADMIN
require_leader_or_above()          # USER_LEADER, MANAGER o ADMIN
```

### Por Permisos
```python
require_permission(Permission.MANAGE_BENEFITS)
require_permission(Permission.GIVE_EXTRA_POINTS)
require_permission(Permission.VIEW_COMPANY_HISTORY)
```

### Factory de Roles
```python
require_roles(Role.ADMIN, Role.MANAGER)  # Cualquiera de los especificados
```

## 🚀 Instalación y Configuración

### 1. Ejecutar Migración
```bash
python run_user_migration.py
```

### 2. Verificar Instalación
La migración crea automáticamente:
- Esquema `puntos_flesan`
- Tabla `users` con estructura completa
- Usuario administrador por defecto
- Índices necesarios

### 3. Usuario Administrador por Defecto
```json
{
    "id": "12345678-1234-5678-9012-123456789012",
    "email": "admin@flesan.com",
    "first_name": "Administrador",
    "last_name": "Sistema",
    "puntos_disponibles": 1000,
    "rol": "admin"
}
```

## 📝 Uso en Endpoints

### Ejemplo: Endpoint que requiere ADMIN
```python
@router.post("/create-manager")
async def create_manager(
    user_data: CreateUserDTO,
    current_user: CurrentUser = Depends(require_admin)
):
    # Solo usuarios ADMIN pueden acceder
    pass
```

### Ejemplo: Endpoint que requiere permiso específico
```python
@router.post("/give-points")
async def give_extra_points(
    points_data: GivePointsDTO,
    current_user: CurrentUser = Depends(require_permission(Permission.GIVE_EXTRA_POINTS))
):
    # Solo usuarios con permiso GIVE_EXTRA_POINTS pueden acceder
    pass
```

### Ejemplo: Validación manual de permisos
```python
@router.get("/team-data")
async def get_team_data(current_user: CurrentUser = Depends(get_current_user)):
    if not current_user.has_permission(Permission.VIEW_TEAM_POINTS):
        raise HTTPException(403, "Sin permisos para ver datos del equipo")
    
    # Lógica del endpoint
    pass
```

## 🔄 Jerarquía de Permisos

```
ADMIN
├── Todos los permisos de MANAGER +
├── create_managers
└── system_config

MANAGER
├── Todos los permisos de USER_LEADER +
├── view_company_history
├── manage_benefits
├── give_extra_points
└── create_users

USER_LEADER
├── Todos los permisos de USER +
├── view_team_points
└── view_team_history

USER
├── redeem_points
├── view_own_points
├── view_own_history
└── view_benefits
```

## 🧪 Testing

### Usuario de Desarrollo
```python
# Automáticamente disponible en modo desarrollo
{
    "id": "12345678-1234-5678-9012-123456789012",
    "email": "dev@flesan.com",
    "first_name": "Usuario",
    "last_name": "Desarrollo",
    "puntos_disponibles": 10000,
    "rol": "admin"
}
```

### Verificar Permisos
```python
user = get_dev_user()
assert user.has_permission(Permission.MANAGE_BENEFITS)
assert user.has_role(Role.ADMIN)
assert user.can_manage_user(Role.MANAGER)
```

## 📊 Próximas Implementaciones

- [ ] Integración con datawarehouse para `user_id`
- [ ] Sistema de equipos y jerarquías
- [ ] Historial de cambios de roles
- [ ] Notificaciones de cambios de permisos
- [ ] Dashboard de administración de usuarios
- [ ] Auditoría de acciones por usuario

## 🔗 Archivos Relacionados

- `app/core/security.py` - Definición de roles y permisos
- `app/infrastructure/auth/dependencies.py` - Dependencies de autorización
- `app/infrastructure/db/models/user_model.py` - Modelo de usuario
- `migrations/002_update_users_table.sql` - Migración de base de datos
- `run_user_migration.py` - Script de migración
