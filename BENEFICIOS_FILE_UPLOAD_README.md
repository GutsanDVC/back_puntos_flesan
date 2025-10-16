# 📁 Manejo de Archivos de Imágenes - Beneficios

## 🎯 Funcionalidad Implementada

Se ha implementado el **manejo completo de archivos de imágenes** para los beneficios, cumpliendo con los siguientes requisitos:

- ✅ **Subida de archivos** en el endpoint de creación
- ✅ **Almacenamiento** en carpeta `static/media/beneficios/`
- ✅ **Servicio público** de imágenes vía URL
- ✅ **Validaciones** de tipo y tamaño de archivo
- ✅ **Limpieza automática** en caso de errores

## 🏗️ Estructura de Archivos

```
static/
└── media/
    └── beneficios/
        ├── uuid1.png
        ├── uuid2.jpg
        └── uuid3.webp
```

## 🌐 Endpoints Actualizados

### 📤 Crear Beneficio con Imagen

**Cambio importante**: Ahora usa `multipart/form-data` en lugar de JSON.

```http
POST /api/v1/beneficios
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- imagen: [archivo de imagen]
- beneficio: "Día Cambio de Casa"
- detalle: "Un día libre para tu cambio de casa"
- regla1: "1 Vez por año"
- regla2: "1 Vez por mes"
- valor: 350
```

### 🖼️ Actualizar Solo Imagen

```http
PUT /api/v1/beneficios/{beneficio_id}/imagen
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- imagen: [nuevo archivo de imagen]
```

### 📁 Servir Imágenes Públicamente

```http
GET /static/media/beneficios/{filename}
```

**Ejemplo de URL generada:**
```
http://localhost:8000/static/media/beneficios/123e4567-e89b-12d3-a456-426614174000.png
```

## 🔒 Validaciones Implementadas

### Tipos de Archivo Permitidos
- `image/jpeg` (.jpg, .jpeg)
- `image/png` (.png)
- `image/gif` (.gif)
- `image/webp` (.webp)

### Restricciones
- **Tamaño máximo**: 5MB
- **Nombre de archivo**: Requerido
- **Extensión**: Debe coincidir con el tipo MIME

## 🛠️ Utilidades Creadas

### FileManager (`app/core/utils/file_utils.py`)

```python
from app.core.utils.file_utils import file_manager

# Guardar imagen
image_url = await file_manager.save_beneficio_image(upload_file)

# Eliminar imagen
deleted = file_manager.delete_beneficio_image(image_url)

# Obtener información
info = file_manager.get_image_info(image_url)
```

## 📝 Ejemplos de Uso

### Con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/beneficios" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "imagen=@/path/to/image.png" \
  -F "beneficio=Día Cambio de Casa" \
  -F "detalle=Un día libre para tu cambio de casa" \
  -F "regla1=1 Vez por año" \
  -F "regla2=1 Vez por mes" \
  -F "valor=350"
```

### Con Python/httpx

```python
import httpx

files = {"imagen": ("beneficio.png", open("image.png", "rb"), "image/png")}
data = {
    "beneficio": "Día Cambio de Casa",
    "detalle": "Un día libre para tu cambio de casa",
    "regla1": "1 Vez por año",
    "regla2": "1 Vez por mes",
    "valor": 350
}

response = httpx.post(
    "http://localhost:8000/api/v1/beneficios",
    files=files,
    data=data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Con JavaScript/FormData

```javascript
const formData = new FormData();
formData.append('imagen', imageFile);
formData.append('beneficio', 'Día Cambio de Casa');
formData.append('detalle', 'Un día libre para tu cambio de casa');
formData.append('regla1', '1 Vez por año');
formData.append('regla2', '1 Vez por mes');
formData.append('valor', '350');

fetch('/api/v1/beneficios', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: formData
});
```

## 🔧 Configuración Técnica

### FastAPI Static Files

```python
# main.py
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Dependencias Requeridas

```txt
# requirements.txt
python-multipart>=0.0.6  # Ya incluido
```

## 🧪 Pruebas

### Verificar Estructura

```bash
python test_file_structure.py
```

### Probar en Swagger UI

1. Iniciar servidor: `uvicorn main:app --reload`
2. Ir a: `http://localhost:8000/docs`
3. Buscar endpoint `POST /api/v1/beneficios`
4. Usar el botón "Try it out"
5. Subir archivo de imagen y llenar campos

## 🔄 Flujo de Procesamiento

1. **Cliente** envía `multipart/form-data` con imagen y datos
2. **FileManager** valida el archivo (tipo, tamaño, extensión)
3. **Sistema** genera nombre único (UUID + extensión)
4. **Archivo** se guarda en `static/media/beneficios/`
5. **URL pública** se genera automáticamente
6. **Base de datos** almacena la URL (no el archivo)
7. **Respuesta** incluye la URL pública de la imagen

## 🚨 Manejo de Errores

### Errores de Validación

```json
{
    "message": "Tipo de archivo no permitido. Solo se permiten imágenes (JPEG, PNG, GIF, WebP)",
    "error_code": "FILE-ERR-001",
    "details": {
        "content_type": "text/plain",
        "allowed_types": ["image/jpeg", "image/png", "image/gif", "image/webp"]
    }
}
```

### Limpieza Automática

Si ocurre un error después de guardar la imagen, el sistema automáticamente:
- Elimina el archivo del disco
- No guarda el registro en la base de datos
- Retorna error apropiado al cliente

## 🔐 Seguridad

### Validaciones Implementadas
- ✅ Verificación de tipo MIME
- ✅ Validación de extensión de archivo
- ✅ Límite de tamaño (5MB)
- ✅ Nombres de archivo únicos (UUID)
- ✅ Directorio restringido

### Consideraciones de Producción
- [ ] Escaneo de malware
- [ ] Compresión automática de imágenes
- [ ] CDN para servir archivos estáticos
- [ ] Backup automático de imágenes

## 📊 Respuesta de Ejemplo

```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "imagen": "/static/media/beneficios/123e4567-e89b-12d3-a456-426614174000.png",
    "beneficio": "Día Cambio de Casa",
    "detalle": "Un día libre para tu cambio de casa",
    "regla1": "1 Vez por año",
    "regla2": "1 Vez por mes",
    "valor": 350,
    "is_active": true,
    "created_at": "2024-10-16T13:30:00Z",
    "updated_at": null
}
```

## 🚀 Estado Actual

✅ **Completamente funcional** y listo para usar
✅ **Validaciones robustas** implementadas
✅ **Manejo de errores** completo
✅ **Documentación** actualizada
✅ **Pruebas** verificadas

---

**¡El sistema de manejo de archivos está listo para migrar y probar! 🎉**
