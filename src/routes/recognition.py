
from flask import Blueprint, render_template, Response, request, redirect, url_for, flash
from models.recognition import detectar_equipo
import cv2
import numpy as np
import os
import mysql.connector
from dotenv import load_dotenv


recognition_bp = Blueprint('recognition', __name__, url_prefix='/reconocimiento')
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'gil_user'),
        password=os.getenv('DB_PASSWORD', 'gil_password_2025'),
        database=os.getenv('DB_NAME', 'gil_laboratorios'),
        port=int(os.getenv('DB_PORT', 3306))
    )

# Abrir la cámara
camera = cv2.VideoCapture(0)

def generar_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Detectar equipo
        nombre, confianza = detectar_equipo(frame)

        # Mostrar el resultado en la pantalla
        if nombre:
            texto = f"{nombre} ({confianza*100:.1f}%)"
            cv2.putText(frame, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convertir a formato web
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# Vista principal: permite mostrar resultados si existen
@recognition_bp.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    equipo_info = None
    if request.method == 'POST':
        if 'imagen' in request.files:
            imagen_file = request.files['imagen']
            if imagen_file.filename != '':
                # Leer imagen en memoria
                file_bytes = np.frombuffer(imagen_file.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                nombre, confianza = detectar_equipo(img)
                if nombre:
                    resultado = f"{nombre} ({confianza*100:.1f}%)"
                    # Buscar en inventario
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM equipos WHERE nombre_equipo LIKE %s LIMIT 1", (f"%{nombre}%",))
                    equipo_info = cursor.fetchone()
                    cursor.close()
                    conn.close()
                else:
                    resultado = "No se reconoció ningún equipo de laboratorio."
    return render_template('reconocimiento.html', resultado=resultado, equipo_info=equipo_info)

@recognition_bp.route('/video')
def video_feed():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')