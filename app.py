from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")  # <- SIN supports_credentials=True

@app.route('/')
def home():
    return jsonify({'status': 'API Nivel 7 Online - NIVEL COMPLETADO'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario', 'desconocido')
    return jsonify({
        'mensaje': 'Login exitoso', 
        'usuario': usuario
    }), 200

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.get_json()
    # Convertimos a float por si React manda texto
    nota1 = float(data.get('nota1', 0))
    nota2 = float(data.get('nota2', 0))
    nota3 = float(data.get('nota3', 0))
    promedio = round((nota1 + nota2 + nota3) / 3, 2)
    return jsonify({'promedio': promedio}), 200
