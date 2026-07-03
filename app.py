from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")

@app.route('/')
def home():
    return jsonify({'status': 'API Nivel 7 Online - MODO PRUEBA'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario', 'desconocido')
    return jsonify({
        'mensaje': 'Login exitoso de prueba', 
        'usuario': usuario,
        'nota': 'CORS FUNCIONA. Ahora metemos la DB'
    }), 200
