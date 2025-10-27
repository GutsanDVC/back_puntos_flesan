-- Migración 003: Crear tabla de historial de canjes
-- Fecha: 2025-01-24
-- Descripción: Tabla para registrar todos los canjes de puntos por beneficios

-- Crear tabla historial_canjes
CREATE TABLE IF NOT EXISTS puntos_flesan.historial_canjes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    beneficio_id INTEGER NOT NULL,
    puntos_canjeados INTEGER NOT NULL,
    fecha_canje TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_uso TIMESTAMP WITH TIME ZONE NOT NULL,
    estado VARCHAR(50) DEFAULT 'ACTIVO' NOT NULL,
    observaciones TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- Constraints
    CONSTRAINT chk_puntos_positivos CHECK (puntos_canjeados > 0),
    CONSTRAINT chk_fecha_uso_valida CHECK (fecha_uso > fecha_canje)
);

-- Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_historial_canjes_user_id ON puntos_flesan.historial_canjes(user_id);
CREATE INDEX IF NOT EXISTS idx_historial_canjes_beneficio_id ON puntos_flesan.historial_canjes(beneficio_id);
CREATE INDEX IF NOT EXISTS idx_historial_canjes_fecha_canje ON puntos_flesan.historial_canjes(fecha_canje);
CREATE INDEX IF NOT EXISTS idx_historial_canjes_fecha_uso ON puntos_flesan.historial_canjes(fecha_uso);
CREATE INDEX IF NOT EXISTS idx_historial_canjes_estado ON puntos_flesan.historial_canjes(estado);

-- Agregar comentarios
COMMENT ON TABLE puntos_flesan.historial_canjes IS 'Registro histórico de canjes de puntos por beneficios';
COMMENT ON COLUMN puntos_flesan.historial_canjes.id IS 'ID único del canje';
COMMENT ON COLUMN puntos_flesan.historial_canjes.user_id IS 'ID del usuario que realiza el canje (del datawarehouse)';
COMMENT ON COLUMN puntos_flesan.historial_canjes.beneficio_id IS 'ID del beneficio canjeado';
COMMENT ON COLUMN puntos_flesan.historial_canjes.puntos_canjeados IS 'Cantidad de puntos utilizados en el canje';
COMMENT ON COLUMN puntos_flesan.historial_canjes.fecha_canje IS 'Fecha y hora en que se realizó el canje';
COMMENT ON COLUMN puntos_flesan.historial_canjes.fecha_uso IS 'Fecha programada para usar el beneficio';
COMMENT ON COLUMN puntos_flesan.historial_canjes.estado IS 'Estado del canje (ACTIVO, USADO, CANCELADO, VENCIDO)';
COMMENT ON COLUMN puntos_flesan.historial_canjes.observaciones IS 'Observaciones adicionales del canje';

-- Verificar que la tabla fue creada correctamente
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'puntos_flesan' AND tablename = 'historial_canjes';
