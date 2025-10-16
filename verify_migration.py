"""Script para verificar que la migración se ejecutó correctamente"""

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def verify_migration():
    """Verifica que la tabla beneficios se haya creado correctamente"""
    print("🔍 Verificando migración de beneficios...")
    
    # Crear engine de base de datos
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    async with engine.begin() as conn:
        try:
            # 1. Verificar esquema actual
            print("\n📋 1. Verificando esquema actual...")
            result = await conn.execute(text("SELECT current_schema()"))
            current_schema = result.scalar()
            print(f"   Esquema actual: {current_schema}")
            
            # 2. Buscar la tabla beneficios en todos los esquemas
            print("\n🔍 2. Buscando tabla 'beneficios' en todos los esquemas...")
            result = await conn.execute(text("""
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE tablename = 'beneficios'
            """))
            tables = result.fetchall()
            
            if tables:
                for schema, table in tables:
                    print(f"   ✅ Encontrada: {schema}.{table}")
            else:
                print("   ❌ Tabla 'beneficios' no encontrada en ningún esquema")
            
            # 3. Verificar migraciones aplicadas
            print("\n📝 3. Verificando migraciones aplicadas...")
            try:
                result = await conn.execute(text("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at"))
                migrations = result.fetchall()
                
                if migrations:
                    print("   Migraciones aplicadas:")
                    for version, applied_at in migrations:
                        print(f"   ✅ {version} - {applied_at}")
                else:
                    print("   ❌ No se encontraron migraciones aplicadas")
            except Exception as e:
                print(f"   ❌ Error al consultar migraciones: {e}")
            
            # 4. Verificar estructura de la tabla si existe
            if tables:
                schema_name = tables[0][0]  # Usar el primer esquema encontrado
                print(f"\n🏗️ 4. Verificando estructura de la tabla en esquema '{schema_name}'...")
                
                result = await conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema_name}' 
                    AND table_name = 'beneficios'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                if columns:
                    print("   Columnas de la tabla:")
                    for col_name, data_type, nullable, default in columns:
                        nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                        default_str = f" DEFAULT {default}" if default else ""
                        print(f"   - {col_name}: {data_type} {nullable_str}{default_str}")
                else:
                    print("   ❌ No se pudieron obtener las columnas de la tabla")
            
            # 5. Verificar índices
            if tables:
                schema_name = tables[0][0]
                print(f"\n📊 5. Verificando índices en esquema '{schema_name}'...")
                
                result = await conn.execute(text(f"""
                    SELECT indexname, indexdef
                    FROM pg_indexes 
                    WHERE schemaname = '{schema_name}' 
                    AND tablename = 'beneficios'
                """))
                indexes = result.fetchall()
                
                if indexes:
                    print("   Índices creados:")
                    for idx_name, idx_def in indexes:
                        print(f"   - {idx_name}")
                else:
                    print("   ❌ No se encontraron índices")
            
            # 6. Contar registros (si hay datos de ejemplo)
            if tables:
                schema_name = tables[0][0]
                print(f"\n📊 6. Contando registros en '{schema_name}.beneficios'...")
                
                try:
                    result = await conn.execute(text(f'SELECT COUNT(*) FROM "{schema_name}".beneficios'))
                    count = result.scalar()
                    print(f"   Total de registros: {count}")
                    
                    if count > 0:
                        result = await conn.execute(text(f'SELECT beneficio, valor FROM "{schema_name}".beneficios LIMIT 3'))
                        samples = result.fetchall()
                        print("   Ejemplos:")
                        for beneficio, valor in samples:
                            print(f"   - {beneficio}: {valor} puntos")
                except Exception as e:
                    print(f"   ❌ Error al contar registros: {e}")
            
        except Exception as e:
            print(f"❌ Error durante la verificación: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()
    
    # 7. Mostrar información de conexión
    print(f"\n🔗 7. Información de conexión:")
    print(f"   Database URL: {settings.DATABASE_URL}")
    
    if not tables:
        print("\n🚨 POSIBLES CAUSAS:")
        print("1. La migración falló silenciosamente")
        print("2. Estás conectado a una base de datos diferente")
        print("3. La tabla se creó en un esquema diferente al que estás viendo")
        print("4. Problemas de permisos")
        
        print("\n🔧 SOLUCIONES:")
        print("1. Verificar configuración de base de datos en .env")
        print("2. Ejecutar migración nuevamente")
        print("3. Verificar permisos del usuario de base de datos")
        print("4. Revisar logs de PostgreSQL")


if __name__ == "__main__":
    asyncio.run(verify_migration())
