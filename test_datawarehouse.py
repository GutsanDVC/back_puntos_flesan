#!/usr/bin/env python3
"""Script de prueba para el módulo de datawarehouse"""

import asyncio
from app.infrastructure.datawarehouse.client import dw_client
from app.application.datawarehouse.services.datawarehouse_service import datawarehouse_service


async def test_datawarehouse():
    """Prueba las funcionalidades básicas del datawarehouse"""
    
    print("🧪 PRUEBAS DEL MÓDULO DATAWAREHOUSE")
    print("=" * 50)
    
    # 1. Test de conexión
    print("\n1. 🔌 Probando conexión...")
    try:
        connection_result = await datawarehouse_service.test_connection()
        print(f"   Estado: {connection_result['status']}")
        print(f"   Mensaje: {connection_result['message']}")
        
        if not connection_result['connected']:
            print("❌ No se pudo conectar al datawarehouse")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de conexión: {e}")
        return False
    
    # 2. Obtener esquemas
    print("\n2. 📋 Obteniendo esquemas disponibles...")
    try:
        schemas = await datawarehouse_service.get_available_schemas()
        print(f"   Esquemas encontrados: {len(schemas)}")
        for schema in schemas[:5]:  # Mostrar solo los primeros 5
            print(f"   - {schema}")
        if len(schemas) > 5:
            print(f"   ... y {len(schemas) - 5} más")
            
    except Exception as e:
        print(f"❌ Error obteniendo esquemas: {e}")
        return False
    
    # 3. Obtener tablas de un esquema (usar el primero disponible)
    if schemas:
        test_schema = schemas[0]
        print(f"\n3. 📊 Obteniendo tablas del esquema '{test_schema}'...")
        try:
            tables = await datawarehouse_service.get_schema_tables(test_schema)
            print(f"   Tablas encontradas: {len(tables)}")
            for table in tables[:3]:  # Mostrar solo las primeras 3
                print(f"   - {table['table_name']} ({table['table_type']})")
            if len(tables) > 3:
                print(f"   ... y {len(tables) - 3} más")
                
        except Exception as e:
            print(f"❌ Error obteniendo tablas: {e}")
            return False
        
        # 4. Obtener estructura de una tabla (usar la primera disponible)
        if tables:
            test_table = tables[0]['table_name']
            print(f"\n4. 🏗️ Obteniendo estructura de '{test_schema}.{test_table}'...")
            try:
                structure = await datawarehouse_service.get_table_structure(test_schema, test_table)
                print(f"   Tabla existe: {structure['exists']}")
                print(f"   Número de filas: {structure['row_count']}")
                print(f"   Columnas: {len(structure['columns'])}")
                
                # Mostrar algunas columnas
                for col in structure['columns'][:3]:
                    print(f"   - {col['column_name']}: {col['data_type']}")
                if len(structure['columns']) > 3:
                    print(f"   ... y {len(structure['columns']) - 3} más")
                    
            except Exception as e:
                print(f"❌ Error obteniendo estructura: {e}")
                return False
            
            # 5. Query simple a la tabla
            print(f"\n5. 🔍 Consultando datos de '{test_schema}.{test_table}'...")
            try:
                # Consulta limitada a 3 registros
                data = await datawarehouse_service.query_table(
                    schema=test_schema,
                    table=test_table,
                    limit=3
                )
                print(f"   Registros obtenidos: {len(data)}")
                
                if data:
                    print("   Primer registro:")
                    first_record = data[0]
                    for key, value in list(first_record.items())[:3]:  # Solo 3 campos
                        print(f"     {key}: {value}")
                    if len(first_record) > 3:
                        print(f"     ... y {len(first_record) - 3} campos más")
                        
            except Exception as e:
                print(f"❌ Error consultando datos: {e}")
                return False
    
    # 6. Query personalizada simple
    print(f"\n6. ⚡ Ejecutando query personalizada...")
    try:
        # Query simple que debería funcionar en cualquier PostgreSQL
        custom_query = "SELECT current_timestamp as now, version() as db_version"
        result = await datawarehouse_service.execute_custom_query(custom_query)
        
        print(f"   Resultado obtenido: {len(result)} fila(s)")
        if result:
            print(f"   Timestamp actual: {result[0]['now']}")
            print(f"   Versión DB: {result[0]['db_version'][:50]}...")
            
    except Exception as e:
        print(f"❌ Error en query personalizada: {e}")
        return False
    
    print(f"\n✅ ¡Todas las pruebas completadas exitosamente!")
    return True


async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del módulo datawarehouse...")
    
    success = await test_datawarehouse()
    
    if success:
        print("\n🎉 ¡Módulo datawarehouse funcionando correctamente!")
        print("\n📋 Endpoints disponibles:")
        print("   GET  /api/v1/datawarehouse/test-connection")
        print("   GET  /api/v1/datawarehouse/schemas")
        print("   GET  /api/v1/datawarehouse/schemas/{schema}/tables")
        print("   GET  /api/v1/datawarehouse/schemas/{schema}/tables/{table}")
        print("   POST /api/v1/datawarehouse/query/custom")
        print("   POST /api/v1/datawarehouse/query/table")
        print("\n🔐 Nota: Todos los endpoints requieren rol ADMIN")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
