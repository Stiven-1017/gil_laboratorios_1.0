from flask import Blueprint, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

equipos_bp = Blueprint('equipos', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'gil_user'),
        password=os.getenv('DB_PASSWORD', 'gil_password_2025'),
        database=os.getenv('DB_NAME', 'gil_laboratorios'),
        port=int(os.getenv('DB_PORT', 3306))
    )

# 🔹 LISTAR TODOS
@equipos_bp.route('/api/equipos', methods=['GET'])
def listar_equipos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipos")
    equipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"equipos": equipos})

# 🔹 OBTENER UNO
@equipos_bp.route('/api/equipos/<int:id>', methods=['GET'])
def obtener_equipo(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id,))
    equipo = cursor.fetchone()
    cursor.close()
    conn.close()
    if equipo:
        return jsonify(equipo)
    return jsonify({"error": "Equipo no encontrado"}), 404

# 🔹 CREAR
@equipos_bp.route('/api/equipos', methods=['POST'])
def crear_equipo():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO equipos (codigo_interno, nombre_equipo, marca, modelo, id_categoria, id_laboratorio, estado_equipo, estado_fisico)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data['codigo_interno'],
        data['nombre_equipo'],
        data.get('marca', ''),
        data.get('modelo', ''),
        data.get('id_categoria', 1),
        data.get('id_laboratorio', 1),
        data.get('estado_equipo', 'disponible'),
        data.get('estado_fisico', 'bueno')
    ))
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": nuevo_id, "mensaje": "Equipo creado"}), 201

# 🔹 ACTUALIZAR
@equipos_bp.route('/api/equipos/<int:id>', methods=['PUT'])
def actualizar_equipo(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE equipos
        SET nombre_equipo=%s, marca=%s, modelo=%s, estado_equipo=%s
        WHERE id_equipo=%s
    """
    cursor.execute(sql, (
        data['nombre_equipo'],
        data.get('marca', ''),
        data.get('modelo', ''),
        data.get('estado_equipo', 'disponible'),
        id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": f"Equipo {id} actualizado"})

# 🔹 ELIMINAR
@equipos_bp.route('/api/equipos/<int:id>', methods=['DELETE'])
def eliminar_equipo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipos WHERE id_equipo=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": f"Equipo {id} eliminado"})