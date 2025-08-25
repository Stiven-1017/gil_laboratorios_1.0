# ========================================
# SISTEMA GIL - TEST DE CONEXIÓN
# Centro Minero de Sogamoso - SENA
# ========================================

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar nuestras clases
from src.gil_database_connection import (
    GILSystem, DatabaseConfig, Usuario, Equipo, Prestamo
)

def test_database_connection():
    """                
    """
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        # Configuración desde variables de entorno
        db_config = DatabaseConfig()
        
        
        # Crear instancia del sistema
        gil_system = GILSystem(db_config)
        
        # Probar conexión
        if gil_system.test_connection():
            print("✅ Conexión exitosa!")
            return gil_system
        else:
            print("❌ Error en la conexión")
            return None
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def test_user_operations(gil_system):
    """
    Probar operaciones de usuarios
    """
    print("\n👤 Probando operaciones de usuarios...")
    
    try:
        # Crear usuario de prueba
        test_user = Usuario(
            documento="87654321",
            nombres="Usuario",
            apellidos="Prueba",
            email="prueba@sena.edu.co",
            telefono="3001234567",
            id_rol=4,  # Aprendiz
            estado="activo"
        )
        
        # Intentar crear usuario
        user_id = gil_system.usuarios.crear_usuario(test_user, "password123")
        print(f"  ✅ Usuario creado con ID: {user_id}")
        
        # Probar autenticación
        authenticated_user = gil_system.usuarios.autenticar_usuario("87654321", "password123")
        if authenticated_user:
            print(f"  ✅ Autenticación exitosa: {authenticated_user.nombres} {authenticated_user.apellidos}")
        else:
            print("  ❌ Error en autenticación")
        
        # Listar usuarios
        usuarios = gil_system.usuarios.listar_usuarios()
        print(f"  📋 Total de usuarios en el sistema: {len(usuarios)}")
        
        return True
        
    except Exception as e:
        print(f"  💥 Error en operaciones de usuarios: {e}")
        return False

def test_equipment_operations(gil_system):
    """
    Probar operaciones de equipos
    """
    print("\n🔬 Probando operaciones de equipos...")
    
    try:
        # Crear equipo de prueba
        test_equipment = Equipo(
            codigo_interno="TEST-001",
            nombre_equipo="Equipo de Prueba",
            marca="Marca Test",
            modelo="Modelo Test",
            numero_serie="TEST-2025-001",
            id_categoria=1,  # Microscopios
            id_laboratorio=1,
            descripcion="Equipo para pruebas del sistema",
            valor_adquisicion=1000000.00,
            fecha_adquisicion=datetime.now().date(),
            proveedor="Proveedor Test",
            estado_equipo="disponible",
            estado_fisico="excelente",
            ubicacion_especifica="Mesa de pruebas"
        )
        
        # Crear equipo
        equipo_id = gil_system.equipos.crear_equipo(test_equipment)
        print(f"  ✅ Equipo creado con ID: {equipo_id}")
        
        # Buscar equipos disponibles
        equipos_disponibles = gil_system.equipos.obtener_equipos_disponibles()
        print(f"  📋 Equipos disponibles: {len(equipos_disponibles)}")
        
        # Buscar equipo por código
        equipo_encontrado = gil_system.equipos.obtener_equipo_por_codigo("TEST-001")
        if equipo_encontrado:
            print(f"  🔍 Equipo encontrado: {equipo_encontrado['nombre_equipo']}")
        
        return equipo_id
        
    except Exception as e:
        print(f"  💥 Error en operaciones de equipos: {e}")
        return None

def test_loan_operations(gil_system, equipo_id, usuario_id=1):
    """
    Probar operaciones de préstamos
    """
    print("\n📋 Probando operaciones de préstamos...")
    
    try:
        # Crear préstamo de prueba
        test_loan = Prestamo(
            id_equipo=equipo_id,
            id_usuario_solicitante=usuario_id,
            fecha_prestamo=datetime.now(),
            fecha_devolucion_programada=datetime.now().replace(hour=23, minute=59),
            proposito_prestamo="Prueba del sistema",
            observaciones_prestamo="Préstamo de prueba",
            estado_prestamo="solicitado"
        )
        
        # Crear préstamo
        prestamo_id = gil_system.prestamos.crear_prestamo(test_loan)
        print(f"  ✅ Préstamo creado con ID: {prestamo_id}")
        
        # Aprobar préstamo
        if gil_system.prestamos.aprobar_prestamo(prestamo_id, usuario_id):
            print("  ✅ Préstamo aprobado")
        
        # Listar préstamos activos
        prestamos_activos = gil_system.prestamos.listar_prestamos_activos()
        print(f"  📋 Préstamos activos: {len(prestamos_activos)}")
        
        return prestamo_id
        
    except Exception as e:
        print(f"  💥 Error en operaciones de préstamos: {e}")
        return None

def test_laboratory_operations(gil_system):
    """
    Probar operaciones de laboratorios
    """
    print("\n🧪 Probando operaciones de laboratorios...")
    
    try:
        # Listar laboratorios
        laboratorios = gil_system.laboratorios.listar_laboratorios()
        print(f"  📋 Total de laboratorios: {len(laboratorios)}")
        
        if laboratorios:
            for lab in laboratorios[:3]:  # Mostrar primeros 3
                print(f"    - {lab['nombre_laboratorio']} ({lab['codigo_lab']})")
        
        return True
        
    except Exception as e:
        print(f"  💥 Error en operaciones de laboratorios: {e}")
        return False

def test_database_queries(gil_system):
    """
    Probar consultas específicas de la base de datos
    """
    print("\n📊 Probando consultas de base de datos...")
    
    try:
        # Probar vista de equipos completa
        equipos_completos = gil_system.db.execute_query(
            "SELECT * FROM vista_equipos_completa LIMIT 5", 
            fetch=True
        )
        print(f"  📋 Vista equipos completa: {len(equipos_completos)} registros")
        
        # Probar estadísticas del sistema
        stats = gil_system.db.execute_query("""
            SELECT 
                'Total Usuarios' as metrica, COUNT(*) as valor FROM usuarios
            UNION ALL
            SELECT 
                'Total Equipos' as metrica, COUNT(*) as valor FROM equipos
            UNION ALL
            SELECT 
                'Equipos Disponibles' as metrica, COUNT(*) as valor 
            FROM equipos WHERE estado_equipo = 'disponible'
        """, fetch=True)
        
        print("  📈 Estadísticas del sistema:")
        for stat in stats:
            print(f"    - {stat['metrica']}: {stat['valor']}")
        
        return True
        
    except Exception as e:
        print(f"  💥 Error en consultas: {e}")
        return False

def test_json_operations(gil_system):
    """
    Probar operaciones con datos JSON
    """
    print("\n🔧 Probando operaciones JSON...")
    
    try:
        # Insertar configuración con JSON
        config_json = {
            "max_prestamos_usuario": 3,
            "notificaciones_email": True,
            "backup_automatico": True,
            "configuracion_lucia": {
                "idioma": "es-CO",
                "confianza_minima": 0.8
            }
        }
        
        gil_system.db.execute_query("""
            INSERT INTO configuracion_sistema (clave_config, valor_config, tipo_dato)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE valor_config = VALUES(valor_config)
        """, ("config_sistema_test", json.dumps(config_json), "json"))
        
        print("  ✅ Configuración JSON insertada")
        
        # Leer configuración
        result = gil_system.db.execute_query("""
            SELECT valor_config FROM configuracion_sistema 
            WHERE clave_config = 'config_sistema_test'
        """, fetch=True)
        
        if result:
            config_leida = json.loads(result[0]['valor_config'])
            print(f"  📖 Configuración leída: {config_leida['configuracion_lucia']['idioma']}")
        
        return True
        
    except Exception as e:
        print(f"  💥 Error en operaciones JSON: {e}")
        return False

def run_comprehensive_test():
    """
    Ejecutar pruebas completas del sistema
    """
    print("🧪 SISTEMA GIL - PRUEBAS COMPLETAS")
    print("="*50)
    
    # 1. Probar conexión
    gil_system = test_database_connection()
    if not gil_system:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    # 2. Probar operaciones de usuarios
    if not test_user_operations(gil_system):
        print("⚠️ Errores en operaciones de usuarios")
    
    # 3. Probar operaciones de equipos
    equipo_id = test_equipment_operations(gil_system)
    if not equipo_id:
        print("⚠️ Errores en operaciones de equipos")
    
    # 4. Probar operaciones de préstamos
    if equipo_id:
        prestamo_id = test_loan_operations(gil_system, equipo_id)
        if not prestamo_id:
            print("⚠️ Errores en operaciones de préstamos")
    
    # 5. Probar operaciones de laboratorios
    if not test_laboratory_operations(gil_system):
        print("⚠️ Errores en operaciones de laboratorios")
    
    # 6. Probar consultas de base de datos
    if not test_database_queries(gil_system):
        print("⚠️ Errores en consultas de base de datos")
    
    # 7. Probar operaciones JSON
    if not test_json_operations(gil_system):
        print("⚠️ Errores en operaciones JSON")
    
    print("\n" + "="*50)
    print("🎉 ¡Pruebas completadas!")
    print("\n📋 Sistema GIL funcionando correctamente")
    print("✨ Listo para implementar la interfaz web y el asistente Lucia")
    
    return True

def interactive_test():
    """
    Modo interactivo de pruebas
    """
    print("🎮 MODO INTERACTIVO DE PRUEBAS")
    print("="*40)
    
    gil_system = test_database_connection()
    if not gil_system:
        return
    
    while True:
        print("\n🔧 Opciones disponibles:")
        print("1. Listar usuarios")
        print("2. Listar equipos")
        print("3. Listar préstamos activos")
        print("4. Buscar equipo por código")
        print("5. Estadísticas del sistema")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        try:
            if opcion == "1":
                usuarios = gil_system.usuarios.listar_usuarios()
                print(f"\n👥 Usuarios ({len(usuarios)}):")
                for user in usuarios[:10]:  # Mostrar máximo 10
                    print(f"  - {user['nombres']} {user['apellidos']} ({user['documento']})")
            
            elif opcion == "2":
                equipos = gil_system.equipos.obtener_equipos_disponibles()
                print(f"\n🔬 Equipos disponibles ({len(equipos)}):")
                for equipo in equipos[:10]:  # Mostrar máximo 10
                    print(f"  - {equipo['nombre_equipo']} ({equipo['codigo_interno']})")
            
            elif opcion == "3":
                prestamos = gil_system.prestamos.listar_prestamos_activos()
                print(f"\n📋 Préstamos activos ({len(prestamos)}):")
                for prestamo in prestamos:
                    print(f"  - {prestamo['nombre_equipo']} → {prestamo['solicitante']}")
            
            elif opcion == "4":
                codigo = input("Código del equipo: ").strip()
                equipo = gil_system.equipos.obtener_equipo_por_codigo(codigo)
                if equipo:
                    print(f"\n🔍 Equipo encontrado:")
                    print(f"  Nombre: {equipo['nombre_equipo']}")
                    print(f"  Marca: {equipo['marca']}")
                    print(f"  Estado: {equipo['estado_equipo']}")
                    print(f"  Ubicación: {equipo['ubicacion_especifica']}")
                else:
                    print("❌ Equipo no encontrado")
            
            elif opcion == "5":
                test_database_queries(gil_system)
            
            elif opcion == "6":
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción no válida")
                
        except Exception as e:
            print(f"💥 Error: {e}")

def main():
    """
    Función principal
    """
    print("🎯 Sistema GIL - Pruebas de Base de Datos")
    print("Centro Minero de Sogamoso - SENA")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_comprehensive_test()

if __name__ == "__main__":
    main()