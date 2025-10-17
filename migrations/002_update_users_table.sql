-- Migración 002: Actualizar tabla de usuarios con nueva estructura
-- Fecha: 2025-10-16
-- Descripción: Actualizar tabla users con campos para sistema de puntos

-- Crear esquema si no existe
CREATE SCHEMA IF NOT EXISTS puntos_flesan;

-- Crear tabla users en el esquema correcto si no existe
CREATE TABLE IF NOT EXISTS puntos_flesan.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    puntos_disponibles INTEGER DEFAULT 0 NOT NULL,
    rol VARCHAR(50) NOT NULL,
    permisos TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_users_email ON puntos_flesan.users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON puntos_flesan.users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_rol ON puntos_flesan.users(rol);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON puntos_flesan.users(is_active);

-- Agregar comentarios a las columnas
COMMENT ON TABLE puntos_flesan.users IS 'Tabla de usuarios del sistema de puntos';
COMMENT ON COLUMN puntos_flesan.users.id IS 'ID primario automático';
COMMENT ON COLUMN puntos_flesan.users.user_id IS 'Número identificatorio del datawarehouse (pendiente implementación)';
COMMENT ON COLUMN puntos_flesan.users.email IS 'Email del usuario';
COMMENT ON COLUMN puntos_flesan.users.first_name IS 'Nombre del usuario';
COMMENT ON COLUMN puntos_flesan.users.last_name IS 'Apellido del usuario';
COMMENT ON COLUMN puntos_flesan.users.puntos_disponibles IS 'Puntos disponibles para canjear';
COMMENT ON COLUMN puntos_flesan.users.rol IS 'Rol del usuario (USER, USER_LEADER, MANAGER, ADMIN)';
COMMENT ON COLUMN puntos_flesan.users.permisos IS 'JSON array de permisos calculados según el rol';
COMMENT ON COLUMN puntos_flesan.users.is_active IS 'Usuario activo';
COMMENT ON COLUMN puntos_flesan.users.created_at IS 'Fecha de creación';
COMMENT ON COLUMN puntos_flesan.users.updated_at IS 'Fecha de última actualización';
COMMENT ON COLUMN puntos_flesan.users.last_login IS 'Fecha de último login';

-- Insertar usuario administrador por defecto para testing
INSERT INTO puntos_flesan.users (
    id,
    user_id,
    email,
    first_name,
    last_name,
    puntos_disponibles,
    rol,
    permisos,
    is_active
) VALUES (
    '12345678-1234-5678-9012-123456789012'::uuid,
    999999,
    'admin@flesan.com',
    'Administrador',
    'Sistema',
    1000,
    'admin',
    '["redeem_points", "view_own_points", "view_own_history", "view_benefits", "view_team_points", "view_team_history", "view_company_history", "manage_benefits", "give_extra_points", "create_users", "create_managers", "system_config"]',
    true
) ON CONFLICT (id) DO UPDATE SET
    user_id = EXCLUDED.user_id,
    email = EXCLUDED.email,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    puntos_disponibles = EXCLUDED.puntos_disponibles,
    rol = EXCLUDED.rol,
    permisos = EXCLUDED.permisos,
    is_active = EXCLUDED.is_active;

-- Verificar que la tabla fue creada correctamente
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'puntos_flesan' AND tablename = 'users';

-- Mostrar estructura de la tabla
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'puntos_flesan' AND table_name = 'users'
ORDER BY ordinal_position;
