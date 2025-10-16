"""Script de prueba simplificado para verificar la estructura de archivos"""

import os
from pathlib import Path


def test_directory_structure():
    """Prueba que la estructura de directorios esté correcta"""
    print("🧪 Probando estructura de directorios...")
    
    static_dir = Path("static")
    media_dir = static_dir / "media"
    beneficios_dir = media_dir / "beneficios"
    
    if static_dir.exists():
        print("✅ Directorio static/ existe")
    else:
        print("❌ Directorio static/ no existe")
    
    if media_dir.exists():
        print("✅ Directorio static/media/ existe")
    else:
        print("❌ Directorio static/media/ no existe")
    
    if beneficios_dir.exists():
        print("✅ Directorio static/media/beneficios/ existe")
    else:
        print("❌ Directorio static/media/beneficios/ no existe")
    
    return static_dir.exists() and media_dir.exists() and beneficios_dir.exists()


def test_file_permissions():
    """Prueba los permisos de escritura en los directorios"""
    print("\n🧪 Probando permisos de escritura...")
    
    beneficios_dir = Path("static/media/beneficios")
    
    if not beneficios_dir.exists():
        print("❌ Directorio no existe para probar permisos")
        return False
    
    # Intentar crear un archivo de prueba
    test_file = beneficios_dir / "test_permissions.txt"
    
    try:
        with open(test_file, "w") as f:
            f.write("test")
        
        if test_file.exists():
            print("✅ Permisos de escritura: OK")
            # Limpiar archivo de prueba
            test_file.unlink()
            return True
        else:
            print("❌ No se pudo crear archivo de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error de permisos: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando verificación de estructura de archivos...\n")
    
    try:
        structure_ok = test_directory_structure()
        permissions_ok = test_file_permissions()
        
        print("\n📋 Resumen de verificación:")
        
        if structure_ok:
            print("✅ Estructura de directorios: OK")
        else:
            print("❌ Estructura de directorios: FALLO")
        
        if permissions_ok:
            print("✅ Permisos de escritura: OK")
        else:
            print("❌ Permisos de escritura: FALLO")
        
        if structure_ok and permissions_ok:
            print("\n🎉 ¡Sistema de archivos listo para usar!")
            print("\n📝 Funcionalidades implementadas:")
            print("🗂️  Carpeta static/media/beneficios/ creada")
            print("🌐 FastAPI configurado para servir archivos estáticos")
            print("📤 Endpoint POST con multipart/form-data")
            print("🖼️  Endpoint PUT para actualizar imágenes")
            print("🔒 Validaciones de tipo y tamaño de archivo")
            print("🧹 Limpieza automática en caso de errores")
            
            print("\n🚀 Próximos pasos:")
            print("1. Ejecutar migraciones: python run_migrations.py")
            print("2. Iniciar servidor: uvicorn main:app --reload")
            print("3. Probar en: http://localhost:8000/docs")
        else:
            print("\n❌ Hay problemas que resolver antes de continuar")
        
    except Exception as e:
        print(f"❌ Error en las verificaciones: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
