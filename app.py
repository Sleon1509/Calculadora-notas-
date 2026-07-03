from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-yaounde-2026')

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)

CORS(app, supports_credentials=True, origins=['https://stackblitz.com', 'https://*.stackblitz.com'])

DB_NAME = '/tmp/notas.db' # /tmp siempre existe en Render

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            nota1 REAL, nota2 REAL, nota3 REAL, nota4 REAL,
            promedio REAL, aprobado INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave) VALUES (?,?)", ('profe', 'yaounde2026'))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error init_db: {e}")

# Ejecutar al importar el archivo
init_db()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios WHERE usuario=? AND clave=?", (usuario, clave))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session.permanent = True
            return jsonify({'mensaje': 'Login exitoso'}), 200
        return jsonify({'error': 'Usuario o clave incorrectos'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calcular', methods=['POST'])
def calcular():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    try:
        notas = [float(data['nota1']), float(data['nota2']), float(data['nota3']), float(data['nota4'])]
        promedio = round(sum(notas) / 4, 2)
        aprobado = 1 if promedio >= 10 else 0
        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO notas (usuario_id, nota1, nota2, nota3, nota4, promedio, aprobado)
                     VALUES (?,?,?,?,?,?,?)''',
                  (session['user_id'], notas[0], notas[1], notas[2], notas[3], promedio, aprobado))
        conn.commit()
        conn.close()
        return jsonify({'promedio': promedio, 'aprobado': bool(aprobado), 'guardado': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'}), 200

@app.route('/')
def home():
    return jsonify({'status': 'API Nivel 7 Online'}), 200
