
# Script para poblar la base de datos GIL con datos de prueba
# Autor: Ronal Stiven Suárez Santiago
# Fecha: 21/08/2025

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno para la conexión
load_dotenv()

try:
    # Conexión a la base de datos
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # --- Insertar laboratorios de prueba ---
    laboratorios = [
        ("LAB-QUI", "Laboratorio de Química", "quimica", "Edificio A - Planta baja", 25, 50.0),
        ("LAB-MIN", "Laboratorio de Minería", "mineria", "Edificio B - Planta alta", 20, 45.0),
        ("LAB-SUE", "Laboratorio de Suelos", "suelos", "Edificio C - Planta baja", 15, 35.0)
    ]

    for lab in laboratorios:
        cursor.execute(
            """
            INSERT IGNORE INTO laboratorios (codigo_lab, nombre_laboratorio, tipo_laboratorio, ubicacion, capacidad_personas, area_m2)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            lab
        )

    # --- Insertar equipos de prueba ---
    equipos = [
        ("EQ-001", "Microscopio Óptico Olympus CX23", "Olympus", "CX23", "SN001", 1, 1, "disponible", "excelente"),
        ("EQ-002", "Balanza Analítica Ohaus EX224", "Ohaus", "EX224", "SN002", 2, 1, "disponible", "bueno"),
        ("EQ-003", "Centrífuga Thermo ST8", "Thermo", "ST8", "SN003", 3, 2, "mantenimiento", "regular"),
        ("EQ-004", "Espectrofotómetro Shimadzu UV-1800", "Shimadzu", "UV-1800", "SN004", 4, 2, "prestado", "bueno"),
        ("EQ-005", "pH-metro Hanna HI2211", "Hanna", "HI2211", "SN005", 5, 3, "disponible", "excelente")
    ]

    for eq in equipos:
        cursor.execute(
            """
            INSERT IGNORE INTO equipos (codigo_interno, nombre_equipo, marca, modelo, numero_serie, id_categoria, id_laboratorio, estado_equipo, estado_fisico)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            eq
        )

    # Confirmar cambios
    conn.commit()
    print("Datos de prueba insertados correctamente en la base de datos.")

except mysql.connector.Error as err:
    print(f"Error al insertar datos de prueba: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()