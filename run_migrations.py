"""Script para ejecutar migraciones de base de datos"""

import asyncio
import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def run_migrations():
    """Ejecuta todas las migraciones pendientes"""
    print("🚀 Iniciando migraciones de base de datos...")
    
    # Crear engine de base de datos
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    # Directorio de migraciones
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print("❌ Directorio de migraciones no encontrado")
        return
    
    # Obtener archivos de migración ordenados
    migration_files = sorted([
        f for f in migrations_dir.glob("*.sql")
        if f.is_file()
    ])
    
    if not migration_files:
        print("ℹ️  No se encontraron archivos de migración")
        return
    
    print(f"📁 Encontrados {len(migration_files)} archivos de migración")
    
    async with engine.begin() as conn:
        # Crear tabla de control de migraciones si no existe
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Verificar qué migraciones ya se ejecutaron
        result = await conn.execute(text(
            "SELECT version FROM schema_migrations"
        ))
        applied_migrations = {row[0] for row in result.fetchall()}
        
        # Ejecutar migraciones pendientes
        for migration_file in migration_files:
            migration_name = migration_file.stem
            
            if migration_name in applied_migrations:
                print(f"⏭️  Saltando migración ya aplicada: {migration_name}")
                continue
            
            print(f"🔄 Ejecutando migración: {migration_name}")
            
            try:
                # Leer y ejecutar el archivo SQL
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Dividir por statements (separados por ;)
                statements = [
                    stmt.strip() 
                    for stmt in sql_content.split(';') 
                    if stmt.strip()
                ]
                
                for statement in statements:
                    if statement:
                        await conn.execute(text(statement))
                
                # Marcar migración como aplicada
                await conn.execute(text(
                    "INSERT INTO schema_migrations (version) VALUES (:version)"
                ), {"version": migration_name})
                
                print(f"✅ Migración completada: {migration_name}")
                
            except Exception as e:
                print(f"❌ Error ejecutando migración {migration_name}: {e}")
                raise
    
    await engine.dispose()
    print("🎉 Todas las migraciones completadas exitosamente!")


if __name__ == "__main__":
    asyncio.run(run_migrations())
