# ========================================
# SISTEMA GIL - SCRIPT DE INSTALACIÓN
# Centro Minero de Sogamoso - SENA
# ========================================

import mysql.connector
from mysql.connector import Error
import os
import sys
import json
from datetime import datetime

class GILInstaller:
    """
    Instalador del sistema GIL
    """
    
    def __init__(self):
        self.connection = None
        self.mysql_version = None
        self.supports_json = False
        
    def connect_to_mysql(self, host='localhost', port=3306, user='root', password=''):
        """
        Conectar a MySQL para instalación
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                print("✓ Conexión a MySQL exitosa")
                self.check_mysql_version()
                return True
                
        except Error as e:
            print(f"✗ Error conectando a MySQL: {e}")
            return False
    
    def check_mysql_version(self):
        """
        Verificar versión de MySQL y capacidades
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT VERSION()")
        version_info = cursor.fetchone()[0]
        self.mysql_version = version_info
        
        print(f"🔍 Versión de MySQL: {version_info}")
        
        # Verificar soporte para JSON (MySQL 5.7.8+)
        version_parts = version_info.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch = int(version_parts[2].split('-')[0])
        
        if major > 5 or (major == 5 and minor > 7) or (major == 5 and minor == 7 and patch >= 8):
            self.supports_json = True
            print("✓ Soporte para tipo JSON disponible")
        else:
            self.supports_json = False
            print("⚠ Tipo JSON no soportado, usando TEXT como alternativa")
        
        cursor.close()
    
    def create_database(self, db_name='gil_laboratorios'):
        """
        Crear base de datos
        """
        try:
            cursor = self.connection.cursor()
            
            # Crear base de datos
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {db_name}
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            
            print(f"✓ Base de datos '{db_name}' creada/verificada")
            
            # Usar la base de datos
            cursor.execute(f"USE {db_name}")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"✗ Error creando base de datos: {e}")
            return False
    
    def get_table_definitions(self):
        """
        Obtener definiciones de tablas según la versión de MySQL
        """
        json_type = "JSON" if self.supports_json else "TEXT"
        
        tables = {
            'roles': f"""
                CREATE TABLE IF NOT EXISTS roles (
                    id_rol INT PRIMARY KEY AUTO_INCREMENT,
                    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
                    descripcion TEXT,
                    permisos {json_type},
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
                )
            """,
            
            'usuarios': """
                CREATE TABLE IF NOT EXISTS usuarios (
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
                )
            """,
            
            'laboratorios': """
                CREATE TABLE IF NOT EXISTS laboratorios (
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
                )
            """,
            
            'categorias_equipos': """
                CREATE TABLE IF NOT EXISTS categorias_equipos (
                    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
                    nombre_categoria VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    codigo_categoria VARCHAR(20) UNIQUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'equipos': f"""
                CREATE TABLE IF NOT EXISTS equipos (
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
                    especificaciones_tecnicas {json_type},
                    valor_adquisicion DECIMAL(12,2),
                    fecha_adquisicion DATE,
                    proveedor VARCHAR(200),
                    garantia_meses INT DEFAULT 12,
                    vida_util_anos INT DEFAULT 5,
                    imagen_url VARCHAR(500),
                    imagen_hash VARCHAR(64),
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
                )
            """,
            
            'prestamos': """
                CREATE TABLE IF NOT EXISTS prestamos (
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
                )
            """,
            
            'tipos_mantenimiento': """
                CREATE TABLE IF NOT EXISTS tipos_mantenimiento (
                    id_tipo_mantenimiento INT PRIMARY KEY AUTO_INCREMENT,
                    nombre_tipo VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    frecuencia_dias INT DEFAULT 30,
                    es_preventivo BOOLEAN DEFAULT true
                )
            """,
            
            'historial_mantenimiento': f"""
                CREATE TABLE IF NOT EXISTS historial_mantenimiento (
                    id_mantenimiento INT PRIMARY KEY AUTO_INCREMENT,
                    id_equipo INT NOT NULL,
                    id_tipo_mantenimiento INT NOT NULL,
                    fecha_mantenimiento DATETIME NOT NULL,
                    tecnico_responsable_id INT,
                    descripcion_trabajo TEXT,
                    partes_reemplazadas {json_type},
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
                )
            """,
            
            'alertas_mantenimiento': """
                CREATE TABLE IF NOT EXISTS alertas_mantenimiento (
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
                )
            """,
            
            'programas_formacion': """
                CREATE TABLE IF NOT EXISTS programas_formacion (
                    id_programa INT PRIMARY KEY AUTO_INCREMENT,
                    codigo_programa VARCHAR(20) NOT NULL UNIQUE,
                    nombre_programa VARCHAR(200) NOT NULL,
                    tipo_programa ENUM('tecnico', 'tecnologo', 'complementaria') NOT NULL,
                    descripcion TEXT,
                    duracion_meses INT,
                    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
                )
            """,
            
            'instructores': f"""
                CREATE TABLE IF NOT EXISTS instructores (
                    id_instructor INT PRIMARY KEY AUTO_INCREMENT,
                    id_usuario INT NOT NULL UNIQUE,
                    especialidad VARCHAR(200),
                    experiencia_anos INT,
                    certificaciones {json_type},
                    fecha_vinculacion DATE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                )
            """,
            
            'practicas_laboratorio': f"""
                CREATE TABLE IF NOT EXISTS practicas_laboratorio (
                    id_practica INT PRIMARY KEY AUTO_INCREMENT,
                    codigo_practica VARCHAR(30) NOT NULL UNIQUE,
                    nombre_practica VARCHAR(200) NOT NULL,
                    id_programa INT NOT NULL,
                    id_laboratorio INT NOT NULL,
                    id_instructor INT NOT NULL,
                    fecha_practica DATETIME NOT NULL,
                    duracion_horas DECIMAL(3,1),
                    numero_estudiantes INT,
                    equipos_requeridos {json_type},
                    materiales_requeridos {json_type},
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
                )
            """,
            
            'comandos_voz': f"""
                CREATE TABLE IF NOT EXISTS comandos_voz (
                    id_comando INT PRIMARY KEY AUTO_INCREMENT,
                    comando_texto VARCHAR(500) NOT NULL,
                    intencion VARCHAR(100) NOT NULL,
                    parametros {json_type},
                    respuesta_esperada TEXT,
                    frecuencia_uso INT DEFAULT 0,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
                )
            """,
            
            'interacciones_voz': """
                CREATE TABLE IF NOT EXISTS interacciones_voz (
                    id_interaccion INT PRIMARY KEY AUTO_INCREMENT,
                    id_usuario INT,
                    comando_detectado TEXT,
                    intencion_identificada VARCHAR(100),
                    confianza_reconocimiento DECIMAL(3,2),
                    respuesta_generada TEXT,
                    accion_ejecutada VARCHAR(200),
                    exitosa BOOLEAN DEFAULT false,
                    timestamp_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duracion_procesamiento_ms INT,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    INDEX idx_usuario_interaccion (id_usuario),
                    INDEX idx_timestamp (timestamp_interaccion)
                )
            """,
            
            'modelos_ia': f"""
                CREATE TABLE IF NOT EXISTS modelos_ia (
                    id_modelo INT PRIMARY KEY AUTO_INCREMENT,
                    nombre_modelo VARCHAR(100) NOT NULL,
                    tipo_modelo ENUM('reconocimiento_imagenes', 'reconocimiento_voz', 'prediccion_mantenimiento') NOT NULL,
                    version_modelo VARCHAR(20),
                    ruta_archivo VARCHAR(500),
                    precision_modelo DECIMAL(5,4),
                    fecha_entrenamiento DATE,
                    fecha_deployment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado_modelo ENUM('activo', 'inactivo', 'entrenando') DEFAULT 'activo',
                    parametros_modelo {json_type}
                )
            """,
            
            'reconocimientos_imagen': f"""
                CREATE TABLE IF NOT EXISTS reconocimientos_imagen (
                    id_reconocimiento INT PRIMARY KEY AUTO_INCREMENT,
                    id_equipo_detectado INT,
                    imagen_original_url VARCHAR(500),
                    confianza_deteccion DECIMAL(3,2),
                    coordenadas_deteccion {json_type},
                    id_modelo_usado INT,
                    procesado_por_usuario INT,
                    fecha_reconocimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    validacion_manual ENUM('correcto', 'incorrecto', 'pendiente') DEFAULT 'pendiente',
                    FOREIGN KEY (id_equipo_detectado) REFERENCES equipos(id_equipo),
                    FOREIGN KEY (id_modelo_usado) REFERENCES modelos_ia(id_modelo),
                    FOREIGN KEY (procesado_por_usuario) REFERENCES usuarios(id_usuario)
                )
            """,
            
            'configuracion_sistema': """
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    id_config INT PRIMARY KEY AUTO_INCREMENT,
                    clave_config VARCHAR(100) NOT NULL UNIQUE,
                    valor_config TEXT,
                    descripcion TEXT,
                    tipo_dato ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """,
            
            'logs_sistema': f"""
                CREATE TABLE IF NOT EXISTS logs_sistema (
                    id_log INT PRIMARY KEY AUTO_INCREMENT,
                    modulo VARCHAR(50) NOT NULL,
                    nivel_log ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
                    mensaje TEXT NOT NULL,
                    id_usuario INT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    datos_adicionales {json_type},
                    timestamp_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    INDEX idx_modulo (modulo),
                    INDEX idx_nivel_log (nivel_log),
                    INDEX idx_timestamp (timestamp_log),
                    INDEX idx_usuario_log (id_usuario)
                )
            """
        }
        
        return tables
    
    def create_tables(self):
        """
        Crear todas las tablas del sistema
        """
        tables = self.get_table_definitions()
        cursor = self.connection.cursor()
        
        # Orden de creación (respetando foreign keys)
        table_order = [
            'roles', 'usuarios', 'laboratorios', 'categorias_equipos', 'equipos',
            'prestamos', 'tipos_mantenimiento', 'historial_mantenimiento',
            'alertas_mantenimiento', 'programas_formacion', 'instructores',
            'practicas_laboratorio', 'comandos_voz', 'interacciones_voz',
            'modelos_ia', 'reconocimientos_imagen', 'configuracion_sistema',
            'logs_sistema'
        ]
        
        print("\n📊 Creando tablas...")
        
        for table_name in table_order:
            try:
                cursor.execute(tables[table_name])
                print(f"  ✓ Tabla '{table_name}' creada")
            except Error as e:
                print(f"  ✗ Error creando tabla '{table_name}': {e}")
                return False
        
        cursor.close()
        return True
    
    def insert_initial_data(self):
        """
        Insertar datos iniciales del sistema
        """
        cursor = self.connection.cursor()
        
        try:
            print("\n📋 Insertando datos iniciales...")
            
            # Roles
            roles_data = [
                ('Administrador', 'Acceso completo al sistema', '{"all": true}'),
                ('Instructor', 'Gestión de prácticas y préstamos', '{"practicas": true, "prestamos": true, "consultas": true}'),
                ('Técnico Laboratorio', 'Mantenimiento y gestión de equipos', '{"equipos": true, "mantenimiento": true, "inventario": true}'),
                ('Aprendiz', 'Consulta de información y solicitud de préstamos', '{"consultas": true, "solicitar_prestamos": true}'),
                ('Coordinador', 'Supervisión y reportes', '{"reportes": true, "supervision": true, "consultas": true}')
            ]
            
            for role in roles_data:
                cursor.execute("""
                    INSERT IGNORE INTO roles (nombre_rol, descripcion, permisos) 
                    VALUES (%s, %s, %s)
                """, role)
            
            print("  ✓ Roles insertados")
            
            # Categorías de equipos
            categorias_data = [
                ('Microscopios', 'Equipos de observación y análisis microscópico', 'MICRO'),
                ('Balanzas', 'Equipos de medición de masa y peso', 'BAL'),
                ('Centrifugas', 'Equipos de separación por centrifugación', 'CENT'),
                ('Espectrofotómetros', 'Equipos de análisis espectral', 'ESPEC'),
                ('pH-metros', 'Equipos de medición de pH', 'PH'),
                ('Estufas', 'Equipos de calentamiento y secado', 'ESTUF'),
                ('Equipos Minería', 'Equipos específicos para análisis minero', 'MIN'),
                ('Equipos Suelos', 'Equipos para análisis de suelos', 'SUELO'),
                ('Instrumentos Medición', 'Instrumentos generales de medición', 'MED'),
                ('Reactivos', 'Productos químicos y reactivos', 'REACT')
            ]
            
            for categoria in categorias_data:
                cursor.execute("""
                    INSERT IGNORE INTO categorias_equipos (nombre_categoria, descripcion, codigo_categoria) 
                    VALUES (%s, %s, %s)
                """, categoria)
            
            print("  ✓ Categorías de equipos insertadas")
            
            # Tipos de mantenimiento
            mantenimiento_data = [
                ('Mantenimiento Preventivo Mensual', 'Revisión general mensual del equipo', 30, True),
                ('Mantenimiento Preventivo Trimestral', 'Mantenimiento detallado trimestral', 90, True),
                ('Calibración', 'Calibración de precisión del equipo', 180, True),
                ('Limpieza Profunda', 'Limpieza y desinfección completa', 15, True),
                ('Mantenimiento Correctivo', 'Reparación por falla o avería', 0, False),
                ('Revisión Anual', 'Inspección completa anual', 365, True)
            ]
            
            for mant in mantenimiento_data:
                cursor.execute("""
                    INSERT IGNORE INTO tipos_mantenimiento (nombre_tipo, descripcion, frecuencia_dias, es_preventivo) 
                    VALUES (%s, %s, %s, %s)
                """, mant)
            
            print("  ✓ Tipos de mantenimiento insertados")
            
            # Programas de formación
            programas_data = [
                ('TEC-MIN-001', 'Tecnología en Minería', 'tecnologo', 'Programa tecnológico en explotación minera', 30),
                ('TEC-QUI-001', 'Tecnología en Química', 'tecnologo', 'Programa tecnológico en análisis químico', 30),
                ('TEC-SUE-001', 'Tecnología en Análisis de Suelos', 'tecnico', 'Programa técnico en análisis y caracterización de suelos', 18),
                ('TEC-MET-001', 'Tecnología en Metalurgia', 'tecnologo', 'Programa tecnológico en procesos metalúrgicos', 30)
            ]
            
            for programa in programas_data:
                cursor.execute("""
                    INSERT IGNORE INTO programas_formacion (codigo_programa, nombre_programa, tipo_programa, descripcion, duracion_meses) 
                    VALUES (%s, %s, %s, %s, %s)
                """, programa)
            
            print("  ✓ Programas de formación insertados")
            
            # Configuración del sistema
            config_data = [
                ('nombre_institucion', 'Centro Minero de Sogamoso - SENA', 'Nombre de la institución', 'string'),
                ('asistente_voz_activo', 'true', 'Activar/desactivar asistente de voz Lucia', 'boolean'),
                ('reconocimiento_imagenes_activo', 'true', 'Activar/desactivar reconocimiento de imágenes', 'boolean'),
                ('precision_minima_reconocimiento', '0.85', 'Precisión mínima para aceptar reconocimiento automático', 'string'),
                ('dias_alerta_mantenimiento', '7', 'Días de anticipación para alertas de mantenimiento', 'integer'),
                ('max_dias_prestamo', '7', 'Máximo de días para préstamos regulares', 'integer'),
                ('email_notificaciones', 'laboratorios@sena.edu.co', 'Email para notificaciones del sistema', 'string')
            ]
            
            for config in config_data:
                cursor.execute("""
                    INSERT IGNORE INTO configuracion_sistema (clave_config, valor_config, descripcion, tipo_dato) 
                    VALUES (%s, %s, %s, %s)
                """, config)
            
            print("  ✓ Configuración del sistema insertada")
            
            # Comandos de voz para Lucia
            comandos_data = [
                ('Lucia buscar equipo', 'buscar_equipo', '{"tipo": "general"}', 'Iniciando búsqueda de equipos disponibles'),
                ('Lucia estado laboratorio', 'consultar_laboratorio', '{"info": "estado"}', 'Consultando estado actual de laboratorios'),
                ('Lucia préstamo equipo', 'solicitar_prestamo', '{"accion": "solicitar"}', 'Iniciando proceso de solicitud de préstamo'),
                ('Lucia inventario disponible', 'consultar_inventario', '{"filtro": "disponible"}', 'Mostrando inventario disponible'),
                ('Lucia alertas mantenimiento', 'consultar_alertas', '{"tipo": "mantenimiento"}', 'Consultando alertas de mantenimiento pendientes'),
                ('Lucia ayuda comandos', 'mostrar_ayuda', '{"seccion": "comandos"}', 'Mostrando comandos disponibles'),
                ('Lucia estado préstamos', 'consultar_prestamos', '{"estado": "activos"}', 'Consultando préstamos activos'),
                ('Lucia registrar devolución', 'devolver_equipo', '{"accion": "devolver"}', 'Iniciando proceso de devolución')
            ]
            
            for comando in comandos_data:
                cursor.execute("""
                    INSERT IGNORE INTO comandos_voz (comando_texto, intencion, parametros, respuesta_esperada) 
                    VALUES (%s, %s, %s, %s)
                """, comando)
            
            print("  ✓ Comandos de voz insertados")
            
            self.connection.commit()
            print("\n✅ Datos iniciales insertados correctamente")
            return True
            
        except Error as e:
            print(f"✗ Error insertando datos iniciales: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def create_views(self):
        """
        Crear vistas del sistema
        """
        cursor = self.connection.cursor()
        
        try:
            print("\n👀 Creando vistas...")
            
            # Vista de equipos completa
            cursor.execute("""
                CREATE OR REPLACE VIEW vista_equipos_completa AS
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
                LEFT JOIN laboratorios l ON e.id_laboratorio = l.id_laboratorio
            """)
            
            print("  ✓ Vista 'vista_equipos_completa' creada")
            
            # Vista de préstamos activos
            cursor.execute("""
                CREATE OR REPLACE VIEW vista_prestamos_activos AS
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
                WHERE p.estado_prestamo = 'activo'
            """)
            
            print("  ✓ Vista 'vista_prestamos_activos' creada")
            
            # Vista de alertas pendientes
            cursor.execute("""
                CREATE OR REPLACE VIEW vista_alertas_pendientes AS
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
                ORDER BY a.prioridad DESC, a.fecha_limite ASC
            """)
            
            print("  ✓ Vista 'vista_alertas_pendientes' creada")
            
            return True
            
        except Error as e:
            print(f"✗ Error creando vistas: {e}")
            return False
        finally:
            cursor.close()
    
    def create_user_and_privileges(self, db_name='gil_laboratorios'):
        """
        Crear usuario específico para la aplicación
        """
        cursor = self.connection.cursor()
        
        try:
            print("\n👤 Creando usuario de aplicación...")
            
            # Crear usuario
            cursor.execute("DROP USER IF EXISTS 'gil_user'@'localhost'")
            cursor.execute("CREATE USER 'gil_user'@'localhost' IDENTIFIED BY 'gil_password_2025'")
            
            # Otorgar privilegios
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO 'gil_user'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            
            print("  ✓ Usuario 'gil_user' creado con privilegios")
            return True
            
        except Error as e:
            print(f"✗ Error creando usuario: {e}")
            return False
        finally:
            cursor.close()
    
    def run_installation(self, mysql_config):
        """
        Ejecutar instalación completa
        """
        print("🚀 Iniciando instalación del Sistema GIL")
        print("="*50)
        
        # Conectar a MySQL
        if not self.connect_to_mysql(**mysql_config):
            return False
        
        # Crear base de datos
        if not self.create_database():
            return False
        
        # Crear tablas
        if not self.create_tables():
            return False
        
        # Insertar datos iniciales
        if not self.insert_initial_data():
            return False
        
        # Crear vistas
        if not self.create_views():
            return False
        
        # Crear usuario de aplicación
        if not self.create_user_and_privileges():
            return False
        
        print("\n" + "="*50)
        print("🎉 ¡Instalación del Sistema GIL completada exitosamente!")
        print("\n📋 Resumen de la instalación:")
        print(f"  📌 Versión MySQL: {self.mysql_version}")
        print(f"  📌 Soporte JSON: {'Sí' if self.supports_json else 'No (usando TEXT)'}")
        print(f"  📌 Base de datos: gil_laboratorios")
        print(f"  📌 Usuario aplicación: gil_user")
        print(f"  📌 Contraseña: gil_password_2025")
        
        print("\n🔧 Configuración para la aplicación Python:")
        print("  DB_HOST=localhost")
        print("  DB_PORT=3306")
        print("  DB_NAME=gil_laboratorios")
        print("  DB_USER=gil_user")
        print("  DB_PASSWORD=gil_password_2025")
        
        print("\n⚡ Próximos pasos:")
        print("  1. Instalar dependencias: pip install -r requirements.txt")
        print("  2. Configurar variables de entorno")
        print("  3. Ejecutar aplicación Python")
        
        return True
    
    def close_connection(self):
        """Cerrar conexión"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Conexión cerrada")

def main():
    """
    Función principal de instalación
    """
    print("🎯 Sistema GIL - Instalador de Base de Datos")
    print("Centro Minero de Sogamoso - SENA")
    print("="*50)
    
    # Solicitar configuración de MySQL
    print("\n🔐 Configuración de MySQL:")
    host = input("Host (localhost): ").strip() or "localhost"
    port = input("Puerto (3306): ").strip() or "3306"
    user = input("Usuario root de MySQL: ").strip() or "root"
    password = input("Contraseña de root: ").strip()
    
    mysql_config = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password
    }
    
    # Crear instalador
    installer = GILInstaller()
    
    try:
        # Ejecutar instalación
        success = installer.run_installation(mysql_config)
        
        if success:
            print("\n✅ Sistema listo para usar!")
            return 0
        else:
            print("\n❌ Error durante la instalación")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Instalación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1
    finally:
        installer.close_connection()

if __name__ == "__main__":
    sys.exit(main())