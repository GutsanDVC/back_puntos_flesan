-- ============================================
-- QUERIES SQL DEL MÓDULO USERS
-- Archivo de referencia/documentación
-- ============================================

-- Crear usuario
INSERT INTO puntos_flesan.users 
(id, email, first_name, last_name, puntos_disponibles, rol, permisos, 
 is_active, created_at, updated_at, last_login)
VALUES 
(:id, :email, :first_name, :last_name, :puntos, :rol, :permisos,
 :is_active, :created_at, :updated_at, :last_login)
RETURNING id, email, first_name, last_name, puntos_disponibles, rol, permisos,
          is_active, created_at, updated_at, last_login;

-- Obtener usuario por ID
SELECT id, email, first_name, last_name, puntos_disponibles, rol, permisos,
       is_active, created_at, updated_at, last_login
FROM puntos_flesan.users
WHERE id = :user_id;

-- Obtener usuario por email
SELECT id, email, first_name, last_name, puntos_disponibles, rol, permisos,
       is_active, created_at, updated_at, last_login
FROM puntos_flesan.users
WHERE email = :email;

-- Actualizar usuario
UPDATE puntos_flesan.users
SET email = :email,
    first_name = :first_name,
    last_name = :last_name,
    puntos_disponibles = :puntos,
    rol = :rol,
    permisos = :permisos,
    is_active = :is_active,
    updated_at = :updated_at
WHERE id = :user_id
RETURNING id, email, first_name, last_name, puntos_disponibles, rol, permisos,
          is_active, created_at, updated_at, last_login;

-- Desactivar usuario (soft delete)
UPDATE puntos_flesan.users
SET is_active = false,
    updated_at = :updated_at
WHERE id = :user_id
RETURNING id;

-- Listar usuarios con filtros
SELECT id, email, first_name, last_name, puntos_disponibles, rol, permisos,
       is_active, created_at, updated_at, last_login
FROM puntos_flesan.users
WHERE 
    (:email IS NULL OR email ILIKE '%' || :email || '%')
    AND (:is_active IS NULL OR is_active = :is_active)
ORDER BY created_at DESC
OFFSET :skip LIMIT :limit;

-- Contar usuarios con filtros
SELECT COUNT(id) as total
FROM puntos_flesan.users
WHERE 
    (:email IS NULL OR email ILIKE '%' || :email || '%')
    AND (:is_active IS NULL OR is_active = :is_active);

-- Verificar si email existe
SELECT COUNT(id) as total
FROM puntos_flesan.users
WHERE email = :email;
