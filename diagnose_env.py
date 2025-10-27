"""Script de diagnostico para problemas con .env"""

import os
from pathlib import Path

print("=" * 70)
print("DIAGNOSTICO DE ARCHIVOS .env")
print("=" * 70)
print()

# 1. Directorio actual
print("[1] DIRECTORIO DE TRABAJO:")
current_dir = Path.cwd()
print(f"   {current_dir}")
print()

# 2. Buscar archivos .env
print("[2] ARCHIVOS .env ENCONTRADOS:")
env_files = list(current_dir.glob("*.env*"))
if env_files:
    for env_file in env_files:
        size = env_file.stat().st_size if env_file.exists() else 0
        print(f"   - {env_file.name} ({size} bytes)")
else:
    print("   [ERROR] No se encontraron archivos .env")
print()

# 3. Verificar contenido del .env
env_path = current_dir / ".env"
if env_path.exists():
    print("[3] CONTENIDO DE .env (CORS_ALLOWED_ORIGINS):")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "CORS_ALLOWED_ORIGINS" in line:
                print(f"   {line.strip()}")
else:
    print("[3] [ERROR] Archivo .env NO EXISTE")
print()

# 4. Verificar variables de entorno del sistema
print("[4] VARIABLE DE ENTORNO DEL SISTEMA:")
sys_cors = os.getenv("CORS_ALLOWED_ORIGINS")
if sys_cors:
    print(f"   CORS_ALLOWED_ORIGINS = {sys_cors}")
    print("   [WARNING] Hay una variable de entorno del sistema!")
    print("   Esta sobrescribe el .env")
else:
    print("   No hay variable CORS_ALLOWED_ORIGINS en el sistema")
print()

# 5. Cargar configuracion
print("[5] CARGANDO CONFIGURACION DE PYDANTIC:")
try:
    from app.core.config import settings
    print(f"   CORS_ALLOWED_ORIGINS = {settings.CORS_ALLOWED_ORIGINS}")
    print(f"   Tipo: {type(settings.CORS_ALLOWED_ORIGINS)}")
    
    if isinstance(settings.CORS_ALLOWED_ORIGINS, list):
        print(f"   Cantidad: {len(settings.CORS_ALLOWED_ORIGINS)}")
        for i, origin in enumerate(settings.CORS_ALLOWED_ORIGINS, 1):
            print(f"      {i}. '{origin}'")
except Exception as e:
    print(f"   [ERROR] {e}")
print()

# 6. Recomendaciones
print("[6] RECOMENDACIONES:")
if not env_path.exists():
    print("   - Crear archivo .env en el directorio raiz del proyecto")
elif sys_cors:
    print("   - Eliminar la variable CORS_ALLOWED_ORIGINS del sistema")
    print("   - O usar: $env:CORS_ALLOWED_ORIGINS=$null (PowerShell)")
else:
    print("   - Verificar que el archivo .env tenga el formato correcto")
    print("   - Reiniciar el servidor completamente")
    print("   - Verificar que no hay espacios extras en el .env")

print()
print("=" * 70)
