from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from routes.recognition import recognition_bp
from routes.equipos import equipos_bp

load_dotenv()

app = Flask(__name__, template_folder='../templates')

@app.route('/mockup/usuarios')
def mockup_usuarios():
    return render_template('mockups/usuarios.html')

@app.route('/mockup/inventario')
def mockup_inventario():
    return render_template('mockups/inventario.html')

@app.route('/mockup/laboratorios')
def mockup_laboratorios():
    return render_template('mockups/laboratorios.html')

@app.route('/mockup/prestamos')
def mockup_prestamos():
    return render_template('mockups/prestamos.html')

@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

@app.route('/prestamos')
def prestamos():
    return render_template('prestamos.html')

@app.route('/laboratorios')
def laboratorios():
    return render_template('laboratorios.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "ok", "message": "Servidor GIL funcionando"})

# Registrar rutas
app.register_blueprint(equipos_bp)
app.register_blueprint(recognition_bp)

if __name__ == '__main__':
    app.run(debug=True)