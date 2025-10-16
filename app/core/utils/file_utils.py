"""Utilidades para manejo de archivos"""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException, status


class FileManager:
    """Gestor de archivos para la aplicación"""
    
    def __init__(self, base_path: str = "static"):
        self.base_path = Path(base_path)
        self.media_path = self.base_path / "media"
        self.beneficios_path = self.media_path / "beneficios"
        
        # Crear directorios si no existen
        self.beneficios_path.mkdir(parents=True, exist_ok=True)
    
    def validate_image_file(self, file: UploadFile) -> None:
        """Valida que el archivo sea una imagen válida"""
        # Validar tipo de contenido
        allowed_types = [
            "image/jpeg", 
            "image/jpg", 
            "image/png", 
            "image/gif", 
            "image/webp"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Tipo de archivo no permitido. Solo se permiten imágenes (JPEG, PNG, GIF, WebP)",
                    "error_code": "FILE-ERR-001",
                    "details": {"content_type": file.content_type, "allowed_types": allowed_types}
                }
            )
        
        # Validar tamaño (máximo 5MB)
        max_size = 5 * 1024 * 1024  # 5MB en bytes
        if hasattr(file, 'size') and file.size and file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": f"Archivo demasiado grande. Tamaño máximo permitido: {max_size // (1024*1024)}MB",
                    "error_code": "FILE-ERR-002",
                    "details": {"file_size": file.size, "max_size": max_size}
                }
            )
        
        # Validar extensión del archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Nombre de archivo requerido",
                    "error_code": "FILE-ERR-003"
                }
            )
        
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Extensión de archivo no permitida",
                    "error_code": "FILE-ERR-004",
                    "details": {"extension": file_extension, "allowed_extensions": allowed_extensions}
                }
            )
    
    async def save_beneficio_image(self, file: UploadFile) -> str:
        """
        Guarda una imagen de beneficio y retorna la URL relativa
        
        Args:
            file: Archivo de imagen subido
            
        Returns:
            str: URL relativa de la imagen guardada
        """
        try:
            # Validar archivo
            self.validate_image_file(file)
            
            # Generar nombre único para el archivo
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Ruta completa donde guardar el archivo
            file_path = self.beneficios_path / unique_filename
            
            # Leer y guardar el archivo
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Retornar URL relativa
            return f"/static/media/beneficios/{unique_filename}"
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Error interno al guardar archivo",
                    "error_code": "FILE-ERR-005",
                    "details": {"internal_error": str(e)}
                }
            )
        finally:
            # Resetear el puntero del archivo para uso posterior si es necesario
            if hasattr(file, 'seek'):
                await file.seek(0)
    
    def delete_beneficio_image(self, image_url: str) -> bool:
        """
        Elimina una imagen de beneficio del sistema de archivos
        
        Args:
            image_url: URL de la imagen a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existía
        """
        try:
            # Extraer el nombre del archivo de la URL
            if not image_url.startswith("/static/media/beneficios/"):
                return False
            
            filename = image_url.split("/")[-1]
            file_path = self.beneficios_path / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_image_info(self, image_url: str) -> Optional[dict]:
        """
        Obtiene información sobre una imagen
        
        Args:
            image_url: URL de la imagen
            
        Returns:
            dict: Información de la imagen o None si no existe
        """
        try:
            if not image_url.startswith("/static/media/beneficios/"):
                return None
            
            filename = image_url.split("/")[-1]
            file_path = self.beneficios_path / filename
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                "filename": filename,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True
            }
            
        except Exception:
            return None


# Instancia global del gestor de archivos
file_manager = FileManager()
