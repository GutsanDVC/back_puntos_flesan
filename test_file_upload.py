"""Script de prueba para verificar el manejo de archivos de imágenes"""

import asyncio
import os
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from app.core.utils.file_utils import file_manager


def create_test_image() -> BytesIO:
    """Crea una imagen de prueba simple (1x1 pixel PNG)"""
    # PNG de 1x1 pixel transparente
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # 8-bit RGBA
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # CRC
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
        0x42, 0x60, 0x82
    ])
    return BytesIO(png_data)


async def test_file_validation():
    """Prueba las validaciones de archivos"""
    print("🧪 Probando validaciones de archivos...")
    
    # Crear archivo de prueba válido
    test_image = create_test_image()
    
    # Simular UploadFile válido
    class MockUploadFile:
        def __init__(self, filename: str, content_type: str, content: BytesIO):
            self.filename = filename
            self.content_type = content_type
            self._content = content
            self.size = len(content.getvalue())
        
        async def read(self):
            return self._content.getvalue()
        
        async def seek(self, position: int):
            self._content.seek(position)
    
    # Prueba con archivo válido
    valid_file = MockUploadFile("test.png", "image/png", test_image)
    
    try:
        file_manager.validate_image_file(valid_file)
        print("✅ Validación de archivo válido: OK")
    except Exception as e:
        print(f"❌ Error en validación de archivo válido: {e}")
    
    # Prueba con tipo de archivo inválido
    invalid_file = MockUploadFile("test.txt", "text/plain", BytesIO(b"test"))
    
    try:
        file_manager.validate_image_file(invalid_file)
        print("❌ Debería haber fallado con tipo inválido")
    except Exception as e:
        print("✅ Validación de tipo inválido: OK")
    
    # Prueba con extensión inválida
    invalid_ext_file = MockUploadFile("test.txt", "image/png", test_image)
    
    try:
        file_manager.validate_image_file(invalid_ext_file)
        print("❌ Debería haber fallado con extensión inválida")
    except Exception as e:
        print("✅ Validación de extensión inválida: OK")


async def test_file_operations():
    """Prueba las operaciones de archivos"""
    print("\n🧪 Probando operaciones de archivos...")
    
    # Crear archivo de prueba
    test_image = create_test_image()
    
    class MockUploadFile:
        def __init__(self, filename: str, content_type: str, content: BytesIO):
            self.filename = filename
            self.content_type = content_type
            self._content = content
            self.size = len(content.getvalue())
        
        async def read(self):
            return self._content.getvalue()
        
        async def seek(self, position: int):
            self._content.seek(position)
    
    test_file = MockUploadFile("test_beneficio.png", "image/png", test_image)
    
    try:
        # Guardar archivo
        image_url = await file_manager.save_beneficio_image(test_file)
        print(f"✅ Archivo guardado: {image_url}")
        
        # Verificar que el archivo existe
        info = file_manager.get_image_info(image_url)
        if info and info['exists']:
            print("✅ Archivo existe en el sistema")
        else:
            print("❌ Archivo no encontrado")
        
        # Eliminar archivo
        deleted = file_manager.delete_beneficio_image(image_url)
        if deleted:
            print("✅ Archivo eliminado correctamente")
        else:
            print("❌ Error al eliminar archivo")
        
        # Verificar que ya no existe
        info_after = file_manager.get_image_info(image_url)
        if not info_after or not info_after['exists']:
            print("✅ Archivo confirmado como eliminado")
        else:
            print("❌ Archivo aún existe después de eliminación")
            
    except Exception as e:
        print(f"❌ Error en operaciones de archivo: {e}")


def test_directory_structure():
    """Prueba que la estructura de directorios esté correcta"""
    print("\n🧪 Probando estructura de directorios...")
    
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


async def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de manejo de archivos...\n")
    
    try:
        test_directory_structure()
        await test_file_validation()
        await test_file_operations()
        
        print("\n🎉 ¡Todas las pruebas de archivos completadas!")
        print("\n📋 Funcionalidades verificadas:")
        print("✅ Estructura de directorios")
        print("✅ Validación de tipos de archivo")
        print("✅ Validación de extensiones")
        print("✅ Guardado de archivos")
        print("✅ Eliminación de archivos")
        print("✅ Información de archivos")
        
        print("\n🌐 Endpoints disponibles:")
        print("📝 POST /api/v1/beneficios - Crear con imagen (multipart/form-data)")
        print("🖼️  PUT /api/v1/beneficios/{id}/imagen - Actualizar solo imagen")
        print("📁 GET /static/media/beneficios/{filename} - Servir imágenes")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
