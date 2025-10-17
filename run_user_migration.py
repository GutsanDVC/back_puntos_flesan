#!/usr/bin/env python3
"""Script para ejecutar la migración de usuarios"""

import asyncio
import os
from sqlalchemy import text
from app.infrastructure.db.session import get_db_session

async def run_user_migration():
    """Ejecuta la migración de usuarios"""
    
    # Leer el archivo de migración
    migration_file = "migrations/002_update_users_table.sql"
    
    if not os.path.exists(migration_file):
        print(f"❌ No se encontró el archivo de migración: {migration_file}")
        return False
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print("🚀 Ejecutando migración de usuarios...")
    
    async with get_db_session() as session:
        try:
            # Dividir el SQL en statements individuales
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement.upper().startswith('--') or not statement:
                    continue
                    
                print(f"📝 Ejecutando statement {i}/{len(statements)}...")
                await session.execute(text(statement))
            
            print("✅ Migración ejecutada exitosamente!")
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando migración: {e}")
            return False

async def verify_migration():
    """Verifica que la migración se ejecutó correctamente"""
    
    print("\n🔍 Verificando migración...")
    
    async with get_db_session() as session:
        try:
            # Verificar que la tabla existe
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'puntos_flesan' 
                    AND table_name = 'users'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ La tabla puntos_flesan.users no existe")
                return False
            
            print("✅ Tabla puntos_flesan.users existe")
            
            # Verificar estructura de la tabla
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'puntos_flesan' AND table_name = 'users'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\n📋 Estructura de la tabla:")
            for col in columns:
                nullable = "NULL" if col.is_nullable == "YES" else "NOT NULL"
                print(f"  - {col.column_name}: {col.data_type} {nullable}")
            
            # Verificar usuario administrador
            result = await session.execute(text("""
                SELECT COUNT(*) FROM puntos_flesan.users 
                WHERE email = 'admin@flesan.com';
            """))
            admin_count = result.scalar()
            
            if admin_count > 0:
                print(f"✅ Usuario administrador creado correctamente")
            else:
                print("⚠️  Usuario administrador no encontrado")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando migración: {e}")
            return False

async def main():
    """Función principal"""
    print("=" * 50)
    print("🔧 MIGRACIÓN DE USUARIOS - SISTEMA DE PUNTOS")
    print("=" * 50)
    
    # Ejecutar migración
    success = await run_user_migration()
    
    if success:
        # Verificar migración
        await verify_migration()
        print("\n🎉 ¡Migración completada exitosamente!")
    else:
        print("\n❌ La migración falló")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
