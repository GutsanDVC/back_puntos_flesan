"""Script para verificar configuracion de CORS"""

from app.core.config import settings

print("=" * 60)
print("VERIFICACION DE CONFIGURACION CORS")
print("=" * 60)
print()

print("[INFO] Configuracion actual:")
print(f"   CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
print(f"   Tipo: {type(settings.CORS_ALLOWED_ORIGINS)}")
print(f"   Es lista: {isinstance(settings.CORS_ALLOWED_ORIGINS, list)}")
print(f"   Cantidad de origenes: {len(settings.CORS_ALLOWED_ORIGINS) if isinstance(settings.CORS_ALLOWED_ORIGINS, list) else 0}")
print()

if isinstance(settings.CORS_ALLOWED_ORIGINS, list):
    print("[OK] Origenes permitidos:")
    for i, origin in enumerate(settings.CORS_ALLOWED_ORIGINS, 1):
        print(f"   {i}. '{origin}'")
    print()
else:
    print("[ERROR] CORS_ALLOWED_ORIGINS no es una lista")
    print()

print("[CONFIG] Configuracion recomendada en .env:")
print("   CORS_ALLOWED_ORIGINS=http://localhost:5000,http://localhost:5173")
print()

print("[INFO] Si el frontend esta en puerto 5173 y backend en 5000:")
print("   - Frontend: http://localhost:5173")
print("   - Backend:  http://localhost:5000")
print()

print("[IMPORTANTE]:")
print("   1. Asegurate de que el .env tenga la variable sin espacios extras")
print("   2. Reinicia el servidor despues de modificar el .env")
print("   3. Verifica que el backend este corriendo en el puerto correcto")
print()

print("=" * 60)
