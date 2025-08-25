
-- ========================================
-- SISTEMA GIL - GESTIÓN INTELIGENTE DE LABORATORIOS
-- Base de datos para Centro Minero de Sogamoso - SENA
-- ========================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS gil_laboratorios
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE gil_laboratorios;

-- ========================================
-- MÓDULO 1: GESTIÓN DE USUARIOS Y ROLES
-- ========================================

-- Tabla de roles
CREATE TABLE roles (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    permisos BIGINT(13),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    documento VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(15),
    id_rol INT,
    password_hash VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    estado ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo',
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- ========================================
-- MÓDULO 2: GESTIÓN DE LABORATORIOS Y ESPACIOS
-- ========================================

-- Tabla de laboratorios
CREATE TABLE laboratorios (
    id_laboratorio INT PRIMARY KEY AUTO_INCREMENT,
    codigo_lab VARCHAR(20) NOT NULL UNIQUE,
    nombre_laboratorio VARCHAR(100) NOT NULL,
    tipo_laboratorio ENUM('quimica', 'mineria', 'suelos', 'metalurgia', 'general') NOT NULL,
    ubicacion VARCHAR(200),
    capacidad_personas INT DEFAULT 20,
    area_m2 DECIMAL(8,2),
    responsable_id INT,
    estado ENUM('disponible', 'ocupado', 'mantenimiento', 'fuera_servicio') DEFAULT 'disponible',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsable_id) REFERENCES usuarios(id_usuario)
);

-- ========================================
-- MÓDULO 3: INVENTARIO INTELIGENTE
-- ========================================

-- Tabla de categorías de equipos
CREATE TABLE categorias_equipos (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre_categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    codigo_categoria VARCHAR(20) UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de equipos
CREATE TABLE equipos (
    id_equipo INT PRIMARY KEY AUTO_INCREMENT,
    codigo_interno VARCHAR(50) NOT NULL UNIQUE,
    codigo_qr VARCHAR(255) UNIQUE,
    nombre_equipo VARCHAR(200) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    numero_serie VARCHAR(150),
    id_categoria INT,
    id_laboratorio INT,
    descripcion TEXT,
    especificaciones_tecnicas BIGINT(13),
    valor_adquisicion DECIMAL(12,2),
    fecha_adquisicion DATE,
    proveedor VARCHAR(200),
    garantia_meses INT DEFAULT 12,
    vida_util_anos INT DEFAULT 5,
    imagen_url VARCHAR(500),
    imagen_hash VARCHAR(64), -- Para reconocimiento de imágenes
    estado_equipo ENUM('disponible', 'prestado', 'mantenimiento', 'reparacion', 'dado_baja') DEFAULT 'disponible',
    estado_fisico ENUM('excelente', 'bueno', 'regular', 'malo') DEFAULT 'bueno',
    ubicacion_especifica VARCHAR(200),
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias_equipos(id_categoria),
    FOREIGN KEY (id_laboratorio) REFERENCES laboratorios(id_laboratorio),
    INDEX idx_codigo_interno (codigo_interno),
    INDEX idx_estado_equipo (estado_equipo),
    INDEX idx_categoria (id_categoria),
    INDEX idx_laboratorio (id_laboratorio)
);

-- ========================================
-- MÓDULO 4: SISTEMA DE PRÉSTAMOS Y TRAZABILIDAD
-- ========================================

-- Tabla de préstamos
CREATE TABLE prestamos (
    id_prestamo INT PRIMARY KEY AUTO_INCREMENT,
    codigo_prestamo VARCHAR(30) NOT NULL UNIQUE,
    id_equipo INT NOT NULL,
    id_usuario_solicitante INT NOT NULL,
    id_usuario_autorizador INT,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_prestamo DATETIME,
    fecha_devolucion_programada DATETIME,
    fecha_devolucion_real DATETIME NULL,
    proposito_prestamo TEXT,
    observaciones_prestamo TEXT,
    observaciones_devolucion TEXT,
    estado_prestamo ENUM('solicitado', 'aprobado', 'rechazado', 'activo', 'devuelto', 'vencido') DEFAULT 'solicitado',
    calificacion_devolucion ENUM('excelente', 'bueno', 'regular', 'malo') NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_usuario_solicitante) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_usuario_autorizador) REFERENCES usuarios(id_usuario),
    INDEX idx_estado_prestamo (estado_prestamo),
    INDEX idx_fecha_prestamo (fecha_prestamo),
    INDEX idx_usuario_solicitante (id_usuario_solicitante)
);

-- ========================================
-- MÓDULO 5: MANTENIMIENTO PREDICTIVO
-- ========================================

-- Tabla de tipos de mantenimiento
CREATE TABLE tipos_mantenimiento (
    id_tipo_mantenimiento INT PRIMARY KEY AUTO_INCREMENT,
    nombre_tipo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    frecuencia_dias INT DEFAULT 30,
    es_preventivo BOOLEAN DEFAULT true
);

-- Tabla de historial de mantenimiento
CREATE TABLE historial_mantenimiento (
    id_mantenimiento INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    id_tipo_mantenimiento INT NOT NULL,
    fecha_mantenimiento DATETIME NOT NULL,
    tecnico_responsable_id INT,
    descripcion_trabajo TEXT,
    partes_reemplazadas BIGINT(13),
    costo_mantenimiento DECIMAL(10,2),
    tiempo_inactividad_horas DECIMAL(5,2),
    observaciones TEXT,
    estado_post_mantenimiento ENUM('excelente', 'bueno', 'regular', 'malo'),
    proxima_fecha_mantenimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_tipo_mantenimiento) REFERENCES tipos_mantenimiento(id_tipo_mantenimiento),
    FOREIGN KEY (tecnico_responsable_id) REFERENCES usuarios(id_usuario),
    INDEX idx_equipo_mantenimiento (id_equipo),
    INDEX idx_fecha_mantenimiento (fecha_mantenimiento)
);

-- Tabla de alertas de mantenimiento
CREATE TABLE alertas_mantenimiento (
    id_alerta INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    tipo_alerta ENUM('mantenimiento_programado', 'mantenimiento_vencido', 'falla_predicha', 'revision_urgente') NOT NULL,
    descripcion_alerta TEXT,
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_limite DATE,
    prioridad ENUM('baja', 'media', 'alta', 'critica') DEFAULT 'media',
    estado_alerta ENUM('pendiente', 'en_proceso', 'resuelta', 'cancelada') DEFAULT 'pendiente',
    asignado_a INT,
    fecha_resolucion DATETIME NULL,
    observaciones_resolucion TEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (asignado_a) REFERENCES usuarios(id_usuario),
    INDEX idx_estado_alerta (estado_alerta),
    INDEX idx_prioridad (prioridad),
    INDEX idx_fecha_limite (fecha_limite)
);

-- ========================================
-- MÓDULO 6: GESTIÓN DE PRÁCTICAS DE LABORATORIO
-- ========================================

-- Tabla de programas de formación
CREATE TABLE programas_formacion (
    id_programa INT PRIMARY KEY AUTO_INCREMENT,
    codigo_programa VARCHAR(20) NOT NULL UNIQUE,
    nombre_programa VARCHAR(200) NOT NULL,
    tipo_programa ENUM('tecnico', 'tecnologo', 'complementaria') NOT NULL,
    descripcion TEXT,
    duracion_meses INT,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de instructores
CREATE TABLE instructores (
    id_instructor INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL UNIQUE,
    especialidad VARCHAR(200),
    experiencia_anos INT,
    certificaciones BIGINT(13),
    fecha_vinculacion DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla de prácticas de laboratorio
CREATE TABLE practicas_laboratorio (
    id_practica INT PRIMARY KEY AUTO_INCREMENT,
    codigo_practica VARCHAR(30) NOT NULL UNIQUE,
    nombre_practica VARCHAR(200) NOT NULL,
    id_programa INT NOT NULL,
    id_laboratorio INT NOT NULL,
    id_instructor INT NOT NULL,
    fecha_practica DATETIME NOT NULL,
    duracion_horas DECIMAL(3,1),
    numero_estudiantes INT,
    equipos_requeridos BIGINT(13), -- Array de IDs de equipos necesarios
    materiales_requeridos BIGINT(13),
    objetivos TEXT,
    descripcion_actividades TEXT,
    observaciones TEXT,
    estado_practica ENUM('programada', 'en_curso', 'completada', 'cancelada') DEFAULT 'programada',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_programa) REFERENCES programas_formacion(id_programa),
    FOREIGN KEY (id_laboratorio) REFERENCES laboratorios(id_laboratorio),
    FOREIGN KEY (id_instructor) REFERENCES instructores(id_instructor),
    INDEX idx_fecha_practica (fecha_practica),
    INDEX idx_estado_practica (estado_practica),
    INDEX idx_laboratorio_practica (id_laboratorio)
);

-- ========================================
-- MÓDULO 7: ASISTENTE DE VOZ LUCIA
-- ========================================

-- Tabla de comandos de voz
CREATE TABLE comandos_voz (
    id_comando INT PRIMARY KEY AUTO_INCREMENT,
    comando_texto VARCHAR(500) NOT NULL,
    intencion VARCHAR(100) NOT NULL,
    parametros BIGINT(13),
    respuesta_esperada TEXT,
    frecuencia_uso INT DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de interacciones de voz
CREATE TABLE interacciones_voz (
    id_interaccion INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    comando_detectado TEXT,
    intencion_identificada VARCHAR(100),
    confianza_reconocimiento DECIMAL(3,2), -- 0.00 a 1.00
    respuesta_generada TEXT,
    accion_ejecutada VARCHAR(200),
    exitosa BOOLEAN DEFAULT false,
    timestamp_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracion_procesamiento_ms INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    INDEX idx_usuario_interaccion (id_usuario),
    INDEX idx_timestamp (timestamp_interaccion)
);

-- ========================================
-- MÓDULO 8: RECONOCIMIENTO DE IMÁGENES
-- ========================================

-- Tabla de modelos de IA
CREATE TABLE modelos_ia (
    id_modelo INT PRIMARY KEY AUTO_INCREMENT,
    nombre_modelo VARCHAR(100) NOT NULL,
    tipo_modelo ENUM('reconocimiento_imagenes', 'reconocimiento_voz', 'prediccion_mantenimiento') NOT NULL,
    version_modelo VARCHAR(20),
    ruta_archivo VARCHAR(500),
    precision_modelo DECIMAL(5,4), -- Precisión del modelo (0.0000 a 1.0000)
    fecha_entrenamiento DATE,
    fecha_deployment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_modelo ENUM('activo', 'inactivo', 'entrenando') DEFAULT 'activo',
    parametros_modelo BIGINT(13)
);

-- Tabla de reconocimientos de imagen
CREATE TABLE reconocimientos_imagen (
    id_reconocimiento INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo_detectado INT,
    imagen_original_url VARCHAR(500),
    confianza_deteccion DECIMAL(3,2), -- 0.00 a 1.00
    coordenadas_deteccion BIGINT(13), -- Coordenadas del bounding box
    id_modelo_usado INT,
    procesado_por_usuario INT,
    fecha_reconocimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validacion_manual ENUM('correcto', 'incorrecto', 'pendiente') DEFAULT 'pendiente',
    FOREIGN KEY (id_equipo_detectado) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_modelo_usado) REFERENCES modelos_ia(id_modelo),
    FOREIGN KEY (procesado_por_usuario) REFERENCES usuarios(id_usuario)
);

-- ========================================
-- MÓDULO 9: CONFIGURACIÓN Y LOGS
-- ========================================

-- Tabla de configuración del sistema
CREATE TABLE configuracion_sistema (
    id_config INT PRIMARY KEY AUTO_INCREMENT,
    clave_config VARCHAR(100) NOT NULL UNIQUE,
    valor_config TEXT,
    descripcion TEXT,
    tipo_dato ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de logs del sistema
CREATE TABLE logs_sistema (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    modulo VARCHAR(50) NOT NULL,
    nivel_log ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    mensaje TEXT NOT NULL,
    id_usuario INT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    datos_adicionales BIGINT(13),
    timestamp_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    INDEX idx_modulo (modulo),
    INDEX idx_nivel_log (nivel_log),
    INDEX idx_timestamp (timestamp_log),
    INDEX idx_usuario_log (id_usuario)
);

-- ========================================
-- INSERCIÓN DE DATOS INICIALES
-- ========================================

-- Insertar roles iniciales
INSERT INTO roles (nombre_rol, descripcion, permisos) VALUES
('Administrador', 'Acceso completo al sistema', 1),
('Instructor', 'Gestión de prácticas y préstamos', 2),
('Técnico Laboratorio', 'Mantenimiento y gestión de equipos', 3),
('Aprendiz', 'Consulta de información y solicitud de préstamos', 4),
('Coordinador', 'Supervisión y reportes', 5);

-- Insertar categorías de equipos iniciales
INSERT INTO categorias_equipos (nombre_categoria, descripcion, codigo_categoria) VALUES
('Microscopios', 'Equipos de observación y análisis microscópico', 'MICRO'),
('Balanzas', 'Equipos de medición de masa y peso', 'BAL'),
('Centrifugas', 'Equipos de separación por centrifugación', 'CENT'),
('Espectrofotómetros', 'Equipos de análisis espectral', 'ESPEC'),
('pH-metros', 'Equipos de medición de pH', 'PH'),
('Estufas', 'Equipos de calentamiento y secado', 'ESTUF'),
('Equipos Minería', 'Equipos específicos para análisis minero', 'MIN'),
('Equipos Suelos', 'Equipos para análisis de suelos', 'SUELO'),
('Instrumentos Medición', 'Instrumentos generales de medición', 'MED'),
('Reactivos', 'Productos químicos y reactivos', 'REACT');

-- Insertar tipos de mantenimiento
INSERT INTO tipos_mantenimiento (nombre_tipo, descripcion, frecuencia_dias, es_preventivo) VALUES
('Mantenimiento Preventivo Mensual', 'Revisión general mensual del equipo', 30, true),
('Mantenimiento Preventivo Trimestral', 'Mantenimiento detallado trimestral', 90, true),
('Calibración', 'Calibración de precisión del equipo', 180, true),
('Limpieza Profunda', 'Limpieza y desinfección completa', 15, true),
('Mantenimiento Correctivo', 'Reparación por falla o avería', 0, false),
('Revisión Anual', 'Inspección completa anual', 365, true);

-- Insertar programas de formación
INSERT INTO programas_formacion (codigo_programa, nombre_programa, tipo_programa, descripcion, duracion_meses) VALUES
('TEC-MIN-001', 'Tecnología en Minería', 'tecnologo', 'Programa tecnológico en explotación minera', 30),
('TEC-QUI-001', 'Tecnología en Química', 'tecnologo', 'Programa tecnológico en análisis químico', 30),
('TEC-SUE-001', 'Tecnología en Análisis de Suelos', 'tecnico', 'Programa técnico en análisis y caracterización de suelos', 18),
('TEC-MET-001', 'Tecnología en Metalurgia', 'tecnologo', 'Programa tecnológico en procesos metalúrgicos', 30);

-- Insertar configuración inicial del sistema
INSERT INTO configuracion_sistema (clave_config, valor_config, descripcion, tipo_dato) VALUES
('nombre_institucion', 'Centro Minero de Sogamoso - SENA', 'Nombre de la institución', 'string'),
('asistente_voz_activo', 'true', 'Activar/desactivar asistente de voz Lucia', 'boolean'),
('reconocimiento_imagenes_activo', 'true', 'Activar/desactivar reconocimiento de imágenes', 'boolean'),
('precision_minima_reconocimiento', '0.85', 'Precisión mínima para aceptar reconocimiento automático', 'string'),
('dias_alerta_mantenimiento', '7', 'Días de anticipación para alertas de mantenimiento', 'integer'),
('max_dias_prestamo', '7', 'Máximo de días para préstamos regulares', 'integer'),
('email_notificaciones', 'laboratorios@sena.edu.co', 'Email para notificaciones del sistema', 'string');

-- Insertar comandos de voz iniciales para Lucia
INSERT INTO comandos_voz (comando_texto, intencion, parametros, respuesta_esperada) VALUES
('Lucia buscar equipo', 'buscar_equipo', 1, 'Iniciando búsqueda de equipos disponibles'),
('Lucia estado laboratorio', 'consultar_laboratorio', 2, 'Consultando estado actual de laboratorios'),
('Lucia préstamo equipo', 'solicitar_prestamo', 3, 'Iniciando proceso de solicitud de préstamo'),
('Lucia inventario disponible', 'consultar_inventario', 4, 'Mostrando inventario disponible'),
('Lucia alertas mantenimiento', 'consultar_alertas', 5, 'Consultando alertas de mantenimiento pendientes'),
('Lucia ayuda comandos', 'mostrar_ayuda', 6, 'Mostrando comandos disponibles'),
('Lucia estado préstamos', 'consultar_prestamos', 7, 'Consultando préstamos activos'),
('Lucia registrar devolución', 'devolver_equipo', 8, 'Iniciando proceso de devolución');

-- ========================================
-- VISTAS ÚTILES PARA CONSULTAS FRECUENTES
-- ========================================

-- Vista de equipos con información completa
CREATE VIEW vista_equipos_completa AS
SELECT 
    e.id_equipo,
    e.codigo_interno,
    e.nombre_equipo,
    e.marca,
    e.modelo,
    c.nombre_categoria,
    l.nombre_laboratorio,
    l.codigo_lab,
    e.estado_equipo,
    e.estado_fisico,
    e.ubicacion_especifica,
    e.fecha_registro,
    CASE 
        WHEN e.estado_equipo = 'prestado' THEN 
            (SELECT CONCAT(u.nombres, ' ', u.apellidos) 
        FROM prestamos p 
        JOIN usuarios u ON p.id_usuario_solicitante = u.id_usuario 
        WHERE p.id_equipo = e.id_equipo AND p.estado_prestamo = 'activo' 
        LIMIT 1)
        ELSE NULL 
    END as usuario_actual
FROM equipos e
LEFT JOIN categorias_equipos c ON e.id_categoria = c.id_categoria
LEFT JOIN laboratorios l ON e.id_laboratorio = l.id_laboratorio;

-- Vista de préstamos activos
CREATE VIEW vista_prestamos_activos AS
SELECT 
    p.id_prestamo,
    p.codigo_prestamo,
    e.codigo_interno,
    e.nombre_equipo,
    CONCAT(u.nombres, ' ', u.apellidos) as solicitante,
    p.fecha_prestamo,
    p.fecha_devolucion_programada,
    DATEDIFF(p.fecha_devolucion_programada, NOW()) as dias_restantes,
    CASE 
        WHEN p.fecha_devolucion_programada < NOW() THEN 'VENCIDO'
        WHEN DATEDIFF(p.fecha_devolucion_programada, NOW()) <= 1 THEN 'POR_VENCER'
        ELSE 'VIGENTE'
    END as estado_temporal
FROM prestamos p
JOIN equipos e ON p.id_equipo = e.id_equipo
JOIN usuarios u ON p.id_usuario_solicitante = u.id_usuario
WHERE p.estado_prestamo = 'activo';

-- Vista de alertas de mantenimiento pendientes
CREATE VIEW vista_alertas_pendientes AS
SELECT 
    a.id_alerta,
    e.codigo_interno,
    e.nombre_equipo,
    l.nombre_laboratorio,
    a.tipo_alerta,
    a.descripcion_alerta,
    a.fecha_limite,
    a.prioridad,
    DATEDIFF(a.fecha_limite, NOW()) as dias_hasta_limite,
    CONCAT(u.nombres, ' ', u.apellidos) as asignado_a
FROM alertas_mantenimiento a
JOIN equipos e ON a.id_equipo = e.id_equipo
LEFT JOIN laboratorios l ON e.id_laboratorio = l.id_laboratorio
LEFT JOIN usuarios u ON a.asignado_a = u.id_usuario
WHERE a.estado_alerta = 'pendiente'
ORDER BY a.prioridad DESC, a.fecha_limite ASC;