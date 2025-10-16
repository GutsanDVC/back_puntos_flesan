#!/usr/bin/env python3
"""Script temporal para probar la configuración"""

try:
    from app.core.config import settings
    print("✅ Configuración cargada correctamente")
    print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    print(f"Tipo: {type(settings.CORS_ALLOWED_ORIGINS)}")
except Exception as e:
    print(f"❌ Error al cargar configuración: {e}")
    import traceback
    traceback.print_exc()
