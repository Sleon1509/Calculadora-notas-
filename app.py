from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-yaounde-2026')

# Configuración de sesión
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)

# CORS para StackBlitz
CORS(app, supports_credentials=True, origins=['https://stackblitz.com', 'https://*.stackblitz.com'])

DB_NAME = 'notas.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabla usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        usuario TEXT UNIQUE NOT NULL,
        clave TEXT NOT NULL
    )''')
    # Tabla notas
    c.execute('''CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER,
        nota1 REAL,
        nota2 REAL,
        nota3 REAL,
        nota4 REAL,
        promedio REAL,
        aprobado INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )''')
    # Crear usuario profe si no existe
    c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave) VALUES (?,?)", ('profe', 'yaounde2026'))
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE usuario =? AND clave =?", (usuario, clave))
    user = c.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['usuario'] = usuario
        session.permanent = True
        return jsonify({'mensaje': 'Login exitoso'}), 200
    return jsonify({'error': 'Usuario o clave incorrectos'}), 401

@app.route('/calcular', methods=['POST'])
def calcular():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    try:
        notas = [float(data['nota1']), float(data['nota2']), float(data['nota3']), float(data['nota4'])]
        promedio = round(sum(notas) / 4, 2)
        aprobado = 1 if promedio >= 10 else 0

        # Guardar en DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO notas (usuario_id, nota1, nota2, nota3, nota4, promedio, aprobado)
                     VALUES (?,?,?,?,?,?,?)''',
                  (session['user_id'], notas[0], notas[1], notas[2], notas[3], promedio, aprobado))
        conn.commit()
        conn.close()

        return jsonify({
            'promedio': promedio,
            'aprobado': bool(aprobado),
            'guardado': True
        }), 200
    except:
        return jsonify({'error': 'Datos inválidos'}), 400

@app.route('/historial', methods=['GET'])
def historial():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT nota1, nota2, nota3, nota4, promedio, aprobado, fecha
                 FROM notas WHERE usuario_id =? ORDER BY fecha DESC LIMIT 10''', (session['user_id'],))
    registros = c.fetchall()
    conn.close()

    historial = []
    for r in registros:
        historial.append({
            'notas': [r[0], r[1], r[2], r[3]],
            'promedio': r[4],
            'aprobado': bool(r[5]),
            'fecha': r[6]
        })
    return jsonify(historial), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=False)
