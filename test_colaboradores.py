#!/usr/bin/env python3
"""Script de prueba para el módulo de colaboradores"""

import asyncio
from app.application.datawarehouse.services.colaboradores_service import colaboradores_service


async def test_colaboradores():
    """Prueba las funcionalidades del módulo de colaboradores"""
    
    print("🧪 PRUEBAS DEL MÓDULO COLABORADORES")
    print("=" * 50)
    
    # 1. Información de la tabla
    print("\n1. 📊 Obteniendo información de la tabla...")
    try:
        info = await colaboradores_service.get_table_info()
        print(f"   Esquema: {info['schema']}")
        print(f"   Tabla: {info['table']}")
        print(f"   Total registros: {info['total_records']}")
        print(f"   Columnas: {info['columns']}")
        print(f"   Campos filtrables: {len(info['filterable_fields'])}")
        print(f"   Columnas por defecto: {len(info['default_columns'])}")
        
        if info['total_records'] == 0:
            print("❌ La tabla no tiene registros")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo información: {e}")
        return False
    
    # 2. Consulta básica (primeros 5 registros)
    print(f"\n2. 📋 Consultando primeros 5 colaboradores...")
    try:
        colaboradores = await colaboradores_service.get_colaboradores(limit=5)
        print(f"   Registros obtenidos: {len(colaboradores)}")
        
        if colaboradores:
            primer_colaborador = colaboradores[0]
            print("   Primer colaborador:")
            print(f"     User ID: {primer_colaborador.get('user_id')}")
            print(f"     Nombre: {primer_colaborador.get('first_name')} {primer_colaborador.get('last_name')}")
            print(f"     Estado: {primer_colaborador.get('empl_status')}")
            print(f"     Centro Costo: {primer_colaborador.get('centro_costo')}")
            print(f"     Correo: {primer_colaborador.get('correo_flesan')}")
            
    except Exception as e:
        print(f"❌ Error en consulta básica: {e}")
        return False
    
    # 3. Filtro por estado activo
    print(f"\n3. ✅ Consultando colaboradores activos...")
    try:
        activos = await colaboradores_service.get_colaboradores_activos(limit=3)
        print(f"   Colaboradores activos encontrados: {len(activos)}")
        
        for colaborador in activos:
            print(f"     - {colaborador.get('first_name')} {colaborador.get('last_name')} (Estado: {colaborador.get('empl_status')})")
            
    except Exception as e:
        print(f"❌ Error consultando activos: {e}")
        return False
    
    # 4. Búsqueda por nombre (si hay datos)
    if colaboradores:
        primer_nombre = colaboradores[0].get('first_name')
        if primer_nombre and len(primer_nombre) >= 2:
            print(f"\n4. 🔍 Buscando colaboradores con nombre que contenga '{primer_nombre[:3]}'...")
            try:
                busqueda = await colaboradores_service.search_colaboradores_by_name(
                    search_term=primer_nombre[:3],
                    limit=3
                )
                print(f"   Resultados de búsqueda: {len(busqueda)}")
                
                for colaborador in busqueda:
                    print(f"     - {colaborador.get('first_name')} {colaborador.get('last_name')}")
                    
            except Exception as e:
                print(f"❌ Error en búsqueda: {e}")
                return False
    
    # 5. Consulta con filtros específicos
    print(f"\n5. 🎯 Consultando con filtros específicos...")
    try:
        # Intentar filtrar por centro de costo si existe
        if colaboradores and colaboradores[0].get('centro_costo'):
            centro_costo = colaboradores[0].get('centro_costo')
            filtrados = await colaboradores_service.get_colaboradores(
                filters={"centro_costo": centro_costo},
                limit=3
            )
            print(f"   Colaboradores en centro de costo '{centro_costo}': {len(filtrados)}")
        else:
            # Filtro genérico por estado
            filtrados = await colaboradores_service.get_colaboradores(
                filters={"empl_status": "A"},
                limit=3
            )
            print(f"   Colaboradores con estado 'A': {len(filtrados)}")
            
    except Exception as e:
        print(f"❌ Error en filtros específicos: {e}")
        return False
    
    # 6. Consulta por user_id específico
    if colaboradores and colaboradores[0].get('user_id'):
        user_id = colaboradores[0].get('user_id')
        print(f"\n6. 👤 Consultando colaborador específico (user_id: {user_id})...")
        try:
            colaborador = await colaboradores_service.get_colaborador_by_user_id(user_id)
            if colaborador:
                print(f"   Colaborador encontrado: {colaborador.get('first_name')} {colaborador.get('last_name')}")
                print(f"   Correo: {colaborador.get('correo_flesan')}")
                print(f"   Departamento: {colaborador.get('nombre_departamento')}")
            else:
                print(f"   Colaborador no encontrado")
                
        except Exception as e:
            print(f"❌ Error consultando por user_id: {e}")
            return False
    
    print(f"\n✅ ¡Todas las pruebas completadas exitosamente!")
    return True


async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del módulo colaboradores...")
    
    success = await test_colaboradores()
    
    if success:
        print("\n🎉 ¡Módulo colaboradores funcionando correctamente!")
        print("\n📋 Endpoints disponibles:")
        print("   GET  /api/v1/colaboradores/")
        print("   POST /api/v1/colaboradores/query")
        print("   GET  /api/v1/colaboradores/user/{user_id}")
        print("   GET  /api/v1/colaboradores/national-id/{national_id}")
        print("   GET  /api/v1/colaboradores/activos")
        print("   GET  /api/v1/colaboradores/centro-costo/{centro_costo}")
        print("   GET  /api/v1/colaboradores/lider/{np_lider}")
        print("   POST /api/v1/colaboradores/search")
        print("   GET  /api/v1/colaboradores/info")
        print("\n🔐 Nota: Todos los endpoints requieren rol ADMIN")
        print("\n📊 Filtros disponibles:")
        print("   - empl_status, user_id, national_id")
        print("   - first_name, last_name, correo_flesan")
        print("   - centro_costo, external_cod_cargo")
        print("   - fecha_ingreso, external_cod_tipo_contrato, np_lider")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración del datawarehouse.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
