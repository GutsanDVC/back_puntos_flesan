-- Script de creación de tabla para historial de canjes
-- Esquema: puntos_flesan
-- Tabla: historial_canjes
-- Comentarios en español según normas del proyecto

-- Crear esquema si no existe
CREATE SCHEMA IF NOT EXISTS puntos_flesan;

-- Crear tipo enumerado para estados si se prefiere (opcional)
-- CREATE TYPE puntos_flesan.canje_estado AS ENUM ('ACTIVO', 'USADO', 'CANCELADO', 'VENCIDO');

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS puntos_flesan.historial_canjes (
    -- Identificador único del canje
    id UUID PRIMARY KEY,

    -- Identificador del usuario (provenido del datawarehouse RRHH)
    user_id INTEGER NOT NULL,

    -- Identificador del beneficio (UUID en tabla puntos_flesan.beneficios)
    beneficio_id UUID NOT NULL,

    -- Cantidad de puntos canjeados en esta operación
    puntos_canjeados INTEGER NOT NULL CHECK (puntos_canjeados > 0),

    -- Fechas de canje y de uso
    fecha_canje TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    fecha_uso   TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    -- Estado del canje (reglas de negocio)
    estado VARCHAR(20) NOT NULL,

    -- Observaciones libres
    observaciones TEXT NULL,

    -- Timestamps de auditoría
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NULL,

    -- Restricción de estados válidos (si no se usa ENUM)
    CONSTRAINT chk_historial_canjes_estado
        CHECK (estado IN ('ACTIVO', 'USADO', 'CANCELADO', 'VENCIDO'))
);

-- Índices para mejorar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_historial_canjes_user_id
    ON puntos_flesan.historial_canjes (user_id);

CREATE INDEX IF NOT EXISTS idx_historial_canjes_beneficio_id
    ON puntos_flesan.historial_canjes (beneficio_id);

CREATE INDEX IF NOT EXISTS idx_historial_canjes_estado
    ON puntos_flesan.historial_canjes (estado);

CREATE INDEX IF NOT EXISTS idx_historial_canjes_fecha_canje
    ON puntos_flesan.historial_canjes (fecha_canje);

-- Llave foránea hacia beneficios (si la tabla existe con UUID como id)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'puntos_flesan' AND table_name = 'beneficios'
    ) THEN
        -- Agregar FK si no existe todavía
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints tc
            WHERE tc.table_schema = 'puntos_flesan'
              AND tc.table_name   = 'historial_canjes'
              AND tc.constraint_type = 'FOREIGN KEY'
              AND tc.constraint_name = 'fk_historial_canjes_beneficio'
        ) THEN
            ALTER TABLE puntos_flesan.historial_canjes
                ADD CONSTRAINT fk_historial_canjes_beneficio
                FOREIGN KEY (beneficio_id)
                REFERENCES puntos_flesan.beneficios (id)
                ON UPDATE NO ACTION
                ON DELETE NO ACTION;
        END IF;
    END IF;
END$$;
