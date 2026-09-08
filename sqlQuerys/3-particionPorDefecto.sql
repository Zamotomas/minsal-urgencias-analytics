-- 1. Crear la partición por defecto
CREATE TABLE atenciones_urgencia_default PARTITION OF atenciones_urgencia DEFAULT;

-- 2. Asegurarnos de que existan las particiones individuales por año
CREATE TABLE IF NOT EXISTS atenciones_urgencia_2021 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2021) TO (2022);

CREATE TABLE IF NOT EXISTS atenciones_urgencia_2022 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2022) TO (2023);

CREATE TABLE IF NOT EXISTS atenciones_urgencia_2023 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2023) TO (2024);

CREATE TABLE IF NOT EXISTS atenciones_urgencia_2024 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2024) TO (2025);

CREATE TABLE IF NOT EXISTS atenciones_urgencia_2025 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2025) TO (2026);