-- Particiones por año
CREATE TABLE atenciones_urgencia_2020 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2020) TO (2021);

CREATE TABLE atenciones_urgencia_2021 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2021) TO (2022);

CREATE TABLE atenciones_urgencia_2022 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2022) TO (2023);

CREATE TABLE atenciones_urgencia_2023 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2023) TO (2024);

CREATE TABLE atenciones_urgencia_2024 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2024) TO (2025);

CREATE TABLE atenciones_urgencia_2025 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2025) TO (2026);

CREATE TABLE atenciones_urgencia_2026 PARTITION OF atenciones_urgencia
    FOR VALUES FROM (2026) TO (2027);

-- Índices de rendimiento
CREATE INDEX idx_urg_fecha ON atenciones_urgencia (fecha);
CREATE INDEX idx_urg_region ON atenciones_urgencia (codigo_region);
CREATE INDEX idx_urg_causa ON atenciones_urgencia (id_causa);
CREATE INDEX idx_urg_comuna ON atenciones_urgencia (codigo_comuna);