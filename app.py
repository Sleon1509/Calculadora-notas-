from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from xhtml2pdf import pisa
import io
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "https://stackblitz.com",
    "https://react-pxfmwada.stackblitz.io"
], expose_headers=["Content-Type", "Set-Cookie"])

app = Flask(__name__)
app.secret_key = 'cambia-esto-en-produccion'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
CORS(app, supports_credentials=True, origins=["https://stackblitz.com", "https://*.stackblitz.io", "https://*.webcontainer.io"])

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alumnos
                 (id INTEGER PRIMARY KEY, nombre TEXT, n1 REAL, n2 REAL, n3 REAL,
                  promedio REAL, estado TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    if data['usuario'] == 'profe' and data['password'] == 'yaounde2026':
        session['logged_in'] = True
        return jsonify({'message': 'Login exitoso'})
    return jsonify({'error': 'Credenciales incorrectas'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    session.pop('logged_in', None)
    return jsonify({'message': 'Logout exitoso'})

@app.route('/api/calcular', methods=['POST'])
@login_required
def api_calcular():
    data = request.json
    nombre = data['nombre']
    n1, n2, n3 = float(data['n1']), float(data['n2']), float(data['n3'])

    if not all(0 <= n <= 20 for n in [n1, n2, n3]):
        return jsonify({'error': 'Notas deben estar entre 0 y 20'}), 400

    promedio = round((n1 + n2 + n3) / 3, 1)
    estado = 'APROBADO' if promedio >= 10 else 'REPROBADO'

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO alumnos (nombre,n1,n2,n3,promedio,estado,fecha) VALUES (?,?,?,?,?,datetime('now','localtime'))",
              (nombre, n1, n2, n3, promedio, estado))
    conn.commit()
    conn.close()

    return jsonify({
        'nombre': nombre,
        'n1': n1, 'n2': n2, 'n3': n3,
        'promedio': promedio,
        'estado': estado
    })

@app.route('/api/historial', methods=['GET'])
@login_required
def api_historial():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT nombre,n1,n2,n3,promedio,estado,fecha FROM alumnos ORDER BY id DESC LIMIT 10")
    alumnos = [{'nombre': r[0], 'n1': r[1], 'n2': r[2], 'n3': r[3],
                'promedio': r[4], 'estado': r[5], 'fecha': r[6]} for r in c.fetchall()]
    conn.close()
    return jsonify(alumnos)

@app.route('/api/borrar', methods=['DELETE'])
@login_required
def api_borrar():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM alumnos")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Historial borrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
