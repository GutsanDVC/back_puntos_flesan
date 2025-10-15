# 🚀 Guía de Despliegue en Servidor

Esta guía detalla cómo desplegar el template de FastAPI en un servidor Linux usando Apache como proxy inverso hacia Nginx, que a su vez hace proxy a Gunicorn ejecutando la aplicación FastAPI.

## 🏗️ Arquitectura de Despliegue

```
Internet → Apache (:80/443) → Nginx (:8080) → Gunicorn (:8001) → FastAPI App
```

## 📋 Prerrequisitos

- Servidor Ubuntu/Debian con acceso root
- Dominio configurado apuntando al servidor
- Python 3.11+
- PostgreSQL (si se usa base de datos)

## 🚀 Despliegue Automático

### Opción 1: Script Automático

```bash
# Clonar el proyecto
git clone <repository-url> /var/www/fastapi_app
cd /var/www/fastapi_app

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con configuraciones reales

# Ejecutar script de despliegue
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh tu-dominio.com
```

### Opción 2: Despliegue Manual

#### 1. Preparar el Servidor

```bash
sudo apt update
sudo apt install python3-venv python3-pip nginx apache2 -y
```

#### 2. Configurar la Aplicación

```bash
cd /var/www/fastapi_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configurar Gunicorn

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Copiar archivo de servicio
sudo cp deploy/fastapi_app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi_app
sudo systemctl start fastapi_app
```

#### 4. Configurar Nginx

```bash
# Copiar configuración
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fastapi_app
sudo sed -i 's/tu-dominio.com/TU_DOMINIO_REAL/g' /etc/nginx/sites-available/fastapi_app

# Activar sitio
sudo ln -s /etc/nginx/sites-available/fastapi_app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Configurar Apache

```bash
# Habilitar módulos necesarios
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod deflate

# Copiar configuración
sudo cp deploy/apache.conf /etc/apache2/sites-available/fastapi.conf
sudo sed -i 's/tu-dominio.com/TU_DOMINIO_REAL/g' /etc/apache2/sites-available/fastapi.conf

# Activar sitio
sudo a2ensite fastapi.conf
sudo a2dissite 000-default.conf
sudo systemctl reload apache2
```

## 🔒 Configurar HTTPS (Opcional pero Recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-apache -y

# Obtener certificado SSL
sudo certbot --apache -d tu-dominio.com

# El certificado se renovará automáticamente
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Logs de la aplicación FastAPI
sudo journalctl -u fastapi_app -f

# Logs de Nginx
sudo tail -f /var/log/nginx/fastapi_error.log

# Logs de Apache
sudo tail -f /var/log/apache2/fastapi_error.log
```

### Comandos Útiles

```bash
# Reiniciar la aplicación
sudo systemctl restart fastapi_app

# Verificar estado de servicios
sudo systemctl status fastapi_app
sudo systemctl status nginx
sudo systemctl status apache2

# Recargar configuración sin reiniciar
sudo systemctl reload nginx
sudo systemctl reload apache2

# Ver configuración activa de Apache
sudo apache2ctl -S
```

## 🔧 Configuración de Entornos

### Variables de Entorno Importantes

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# Autenticación
AUTH_JWKS_URL=https://tu-auth-server.com/.well-known/jwks.json
AUTH_AUDIENCE=tu-api-audience
AUTH_ISSUER=https://tu-auth-server.com/
SECRET_KEY=tu-clave-secreta-muy-segura

# Configuración de la aplicación
LOG_LEVEL=INFO
CORS_ALLOWED_ORIGINS=https://tu-frontend.com,https://otro-dominio.com
```

### Configuración por Ambiente

#### Desarrollo (DS)
- Dominio: `fastds.grupoflesan.com`
- LOG_LEVEL: `DEBUG`
- Base de datos de desarrollo

#### QA
- Dominio: `fastqa.grupoflesan.com`
- LOG_LEVEL: `INFO`
- Base de datos de testing

#### Producción (PROD)
- Dominio: `fastapi.grupoflesan.com`
- LOG_LEVEL: `WARNING`
- Base de datos de producción
- HTTPS obligatorio

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error 502 Bad Gateway
```bash
# Verificar que Gunicorn esté ejecutándose
sudo systemctl status fastapi_app

# Verificar logs de Nginx
sudo tail -f /var/log/nginx/fastapi_error.log
```

#### 2. Error de Permisos
```bash
# Asegurar permisos correctos
sudo chown -R www-data:www-data /var/www/fastapi_app
sudo chmod -R 755 /var/www/fastapi_app
```

#### 3. Error de Base de Datos
```bash
# Verificar conexión a PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Verificar variables de entorno
cat /var/www/fastapi_app/.env
```

#### 4. Puerto en Uso
```bash
# Verificar qué procesos usan los puertos
sudo netstat -tlnp | grep :8001
sudo netstat -tlnp | grep :8080
```

### Logs de Depuración

```bash
# Habilitar logs detallados temporalmente
sudo systemctl edit fastapi_app

# Agregar:
[Service]
Environment="LOG_LEVEL=DEBUG"

# Reiniciar servicio
sudo systemctl restart fastapi_app
```

## 📈 Optimización de Rendimiento

### Configuración de Gunicorn

El archivo `gunicorn.conf.py` incluye configuraciones optimizadas:
- Workers: `CPU cores * 2 + 1`
- Worker class: `uvicorn.workers.UvicornWorker`
- Timeouts configurados apropiadamente

### Configuración de Nginx

- Proxy buffering habilitado
- Compresión gzip
- Headers de seguridad
- Cache para archivos estáticos

### Configuración de Apache

- Compresión DEFLATE
- Headers de seguridad
- Configuración de proxy optimizada

## 🔄 Actualizaciones

### Proceso de Actualización

```bash
# 1. Hacer backup de la configuración actual
sudo cp .env .env.backup

# 2. Actualizar código
git pull origin main

# 3. Actualizar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar aplicación
sudo systemctl restart fastapi_app

# 5. Verificar que todo funcione
curl -f http://localhost:8001/health/
```

### Rollback en Caso de Error

```bash
# Volver a versión anterior
git checkout HEAD~1

# Restaurar configuración
sudo cp .env.backup .env

# Reiniciar servicios
sudo systemctl restart fastapi_app
```
