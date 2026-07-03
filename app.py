from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "https://stackblitz.com",
    "https://react-pxfmwada.stackblitz.io"
])

app.secret_key = 'cambia-esto-en-produccion'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('usuario') == 'profe' and data.get('clave') == 'yaounde2026':
        session['usuario'] = 'profe'
        return jsonify({"mensaje": "Login exitoso"})
    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/calcular', methods=['POST'])
def calcular():
    if 'usuario' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    try:
        notas = [float(data['nota1']), float(data['nota2']), float(data['nota3']), float(data['nota4'])]
        promedio = sum(notas) / len(notas)
        return jsonify({
            "promedio": round(promedio, 2),
            "aprobado": promedio >= 10.5
        })
    except:
        return jsonify({"error": "Datos inválidos"}), 400

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada"})
