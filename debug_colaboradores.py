#!/usr/bin/env python3
"""Script simple para debug de colaboradores"""

import asyncio
import sys

async def test_imports():
    """Prueba las importaciones paso a paso"""
    
    print("🔍 DEBUG - Probando importaciones...")
    
    try:
        print("1. Importando configuración...")
        from app.core.config import settings
        print(f"   ✅ Configuración cargada")
        print(f"   DATABASE_URL_DW configurada: {bool(settings.DATABASE_URL_DW)}")
        
        print("\n2. Importando excepciones datawarehouse...")
        from app.infrastructure.datawarehouse.exceptions import DatawarehouseException
        print("   ✅ Excepciones importadas")
        
        print("\n3. Importando conexión datawarehouse...")
        from app.infrastructure.datawarehouse.connection import dw_connection
        print(f"   ✅ Conexión importada: {dw_connection is not None}")
        
        print("\n4. Importando cliente datawarehouse...")
        from app.infrastructure.datawarehouse.client import dw_client
        print(f"   ✅ Cliente importado: {dw_client is not None}")
        
        print("\n5. Importando servicio colaboradores...")
        from app.application.datawarehouse.services.colaboradores_service import colaboradores_service
        print(f"   ✅ Servicio importado: {colaboradores_service is not None}")
        
        if colaboradores_service is not None:
            print("\n6. Probando info de tabla...")
            info = await colaboradores_service.get_table_info()
            print(f"   ✅ Info obtenida - Total registros: {info['total_records']}")
            
            print("\n7. Probando consulta simple...")
            result = await colaboradores_service.get_colaboradores(limit=1)
            print(f"   ✅ Consulta exitosa - Registros: {len(result)}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal"""
    print("🚀 Iniciando debug de colaboradores...")
    
    success = await test_imports()
    
    if success:
        print("\n✅ ¡Debug completado exitosamente!")
        print("\nPuedes probar el endpoint:")
        print("curl -X GET 'http://localhost:8000/api/v1/colaboradores/debug?limit=1'")
    else:
        print("\n❌ Debug falló. Revisa los errores arriba.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
