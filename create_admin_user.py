#!/usr/bin/env python3
"""Script para crear el usuario administrador"""

import asyncio
from sqlalchemy import text
from app.infrastructure.db.session import get_db_session

async def create_admin_user():
    """Crea el usuario administrador"""
    
    print("🔧 Creando usuario administrador...")
    
    async with get_db_session() as session:
        try:
            # Insertar usuario administrador
            await session.execute(text("""
                INSERT INTO puntos_flesan.users (
                    id,
                    user_id,
                    email,
                    first_name,
                    last_name,
                    puntos_disponibles,
                    rol,
                    permisos,
                    is_active,
                    created_at
                ) VALUES (
                    '12345678-1234-5678-9012-123456789012'::uuid,
                    999999,
                    'admin@flesan.com',
                    'Administrador',
                    'Sistema',
                    1000,
                    'admin',
                    '["redeem_points", "view_own_points", "view_own_history", "view_benefits", "view_team_points", "view_team_history", "view_company_history", "manage_benefits", "give_extra_points", "create_users", "create_managers", "system_config"]',
                    true,
                    CURRENT_TIMESTAMP
                ) ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    email = EXCLUDED.email,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    puntos_disponibles = EXCLUDED.puntos_disponibles,
                    rol = EXCLUDED.rol,
                    permisos = EXCLUDED.permisos,
                    is_active = EXCLUDED.is_active,
                    created_at = EXCLUDED.created_at;
            """))
            
            print("✅ Usuario administrador creado exitosamente!")
            
            # Verificar que se creó
            result = await session.execute(text("""
                SELECT email, first_name, last_name, puntos_disponibles, rol 
                FROM puntos_flesan.users 
                WHERE email = 'admin@flesan.com';
            """))
            user = result.fetchone()
            
            if user:
                print(f"📋 Usuario creado: {user.first_name} {user.last_name}")
                print(f"📧 Email: {user.email}")
                print(f"🎭 Rol: {user.rol}")
                print(f"💰 Puntos: {user.puntos_disponibles}")
            else:
                print("❌ No se pudo verificar la creación del usuario")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando usuario administrador: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(create_admin_user())
    if success:
        print("\n🎉 ¡Usuario administrador listo!")
    else:
        print("\n❌ Falló la creación del usuario administrador")
