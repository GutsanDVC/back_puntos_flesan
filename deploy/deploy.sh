#!/bin/bash

# Script de despliegue automatizado para FastAPI
# Uso: ./deploy.sh [dominio] [nombre-proyecto]

set -e

# Detectar directorio actual y nombre del proyecto
CURRENT_DIR=$(pwd)
PROJECT_NAME=$(basename "$CURRENT_DIR")

# Configuración
DOMAIN=${1:-"tu-dominio.com"}
APP_NAME=${2:-"$PROJECT_NAME"}
APP_DIR="$CURRENT_DIR"
SERVICE_NAME="${APP_NAME}_service"

echo "🚀 Iniciando despliegue de $APP_NAME para dominio: $DOMAIN"
echo "📁 Directorio del proyecto: $APP_DIR"
echo "⚙️ Nombre del servicio: $SERVICE_NAME"

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# 1. Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
apt update
apt install -y python3-venv python3-pip nginx apache2

# 2. Crear directorio de logs para Gunicorn
echo "📁 Creando directorios de logs..."
mkdir -p /var/log/gunicorn
chown www-data:www-data /var/log/gunicorn

# 3. Configurar permisos del directorio de la aplicación
echo "🔐 Configurando permisos..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# 4. Instalar dependencias de Python (si no están instaladas)
if [ ! -d "$APP_DIR/venv" ]; then
    echo "🐍 Creando entorno virtual..."
    cd $APP_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# 5. Configurar servicio systemd
echo "⚙️ Configurando servicio systemd..."
cp deploy/fastapi_app.service /etc/systemd/system/${SERVICE_NAME}.service
sed -i "s|/var/www/fastapi_app|$APP_DIR|g" /etc/systemd/system/${SERVICE_NAME}.service
sed -i "s|fastapi_app|$SERVICE_NAME|g" /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# 6. Configurar Nginx
echo "🌐 Configurando Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/${APP_NAME}
sed -i "s/tu-dominio.com/$DOMAIN/g" /etc/nginx/sites-available/${APP_NAME}
sed -i "s/fastapi_app/$APP_NAME/g" /etc/nginx/sites-available/${APP_NAME}
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# 7. Configurar Apache
echo "🔧 Configurando Apache..."
a2enmod proxy
a2enmod proxy_http
a2enmod headers
a2enmod deflate
cp deploy/apache.conf /etc/apache2/sites-available/${APP_NAME}.conf
sed -i "s/tu-dominio.com/$DOMAIN/g" /etc/apache2/sites-available/${APP_NAME}.conf
sed -i "s/fastapi_app/$APP_NAME/g" /etc/apache2/sites-available/${APP_NAME}.conf
a2ensite ${APP_NAME}.conf
a2dissite 000-default.conf

# 8. Reiniciar servicios
echo "🔄 Reiniciando servicios..."
systemctl restart $SERVICE_NAME
systemctl restart nginx
systemctl reload apache2

# 9. Verificar estado de servicios
echo "✅ Verificando estado de servicios..."
systemctl status $SERVICE_NAME --no-pager
systemctl status nginx --no-pager
systemctl status apache2 --no-pager

# 10. Mostrar información de acceso
echo ""
echo "🎉 ¡Despliegue completado!"
echo "📍 Proyecto: $APP_NAME"
echo "📍 URL: http://$DOMAIN"
echo "📋 Documentación: http://$DOMAIN/docs"
echo "❤️ Health Check: http://$DOMAIN/health/"
echo ""
echo "📊 Para ver logs:"
echo "   $APP_NAME: journalctl -u $SERVICE_NAME -f"
echo "   Nginx: tail -f /var/log/nginx/${APP_NAME}_error.log"
echo "   Apache: tail -f /var/log/apache2/${APP_NAME}_error.log"
echo ""
echo "🔧 Para reiniciar la aplicación:"
echo "   sudo systemctl restart $SERVICE_NAME"
