-- Migración para crear tabla de beneficios
-- Fecha: 2024-10-16
-- Descripción: Crear tabla beneficios con todos los campos requeridos

CREATE TABLE IF NOT EXISTS puntos_flesan.beneficios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imagen VARCHAR(500) NOT NULL,
    beneficio VARCHAR(200) NOT NULL,
    detalle TEXT NOT NULL,
    regla1 VARCHAR(200) NOT NULL,
    regla2 VARCHAR(200) NOT NULL,
    valor INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_beneficios_beneficio ON puntos_flesan.beneficios(beneficio);
CREATE INDEX IF NOT EXISTS idx_beneficios_is_active ON puntos_flesan.beneficios(is_active);
CREATE INDEX IF NOT EXISTS idx_beneficios_created_at ON puntos_flesan.beneficios(created_at);
CREATE INDEX IF NOT EXISTS idx_beneficios_valor ON puntos_flesan.beneficios(valor);

-- -- Insertar datos de ejemplo
-- INSERT INTO beneficios (imagen, beneficio, detalle, regla1, regla2, valor, is_active) VALUES
-- ('host/media/beneficios/CambiodeCasa.png', 'Día Cambio de Casa', 'Un día libre para tu cambio de casa', '1 Vez por año', '1 Vez por mes', 350, true),
-- ('host/media/beneficios/DiaCumpleanos.png', 'Día de Cumpleaños', 'Día libre por tu cumpleaños', '1 Vez por año', 'Solo en tu cumpleaños', 200, true),
-- ('host/media/beneficios/DiaMatrimonio.png', 'Día de Matrimonio', 'Día libre para tu matrimonio', '1 Vez en la vida', 'Con 30 días de anticipación', 500, true),
-- ('host/media/beneficios/HoraSalida.png', 'Hora de Salida Temprana', 'Salir 2 horas antes del trabajo', '2 Veces por mes', 'Con autorización previa', 100, true),
-- ('host/media/beneficios/AlmuerzoGratis.png', 'Almuerzo Gratis', 'Almuerzo gratuito en el casino', '1 Vez por semana', 'Solo días laborales', 150, true)
-- ON CONFLICT (beneficio) DO NOTHING;
