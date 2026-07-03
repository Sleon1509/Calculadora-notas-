from flask import Flask, request, session, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-cambiar')

USUARIO = 'profe'
CLAVE = 'yaounde2026'

def init_db():
    conn = sqlite3.connect('notas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registros
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT NOT NULL,
                  n1 REAL NOT NULL,
                  n2 REAL NOT NULL,
                  n3 REAL NOT NULL,
                  promedio REAL NOT NULL,
                  fecha TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['clave'] == CLAVE:
            session['logueado'] = True
            return redirect(url_for('home'))
        error = 'Usuario o clave incorrectos'
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
        body { font-family: Arial; background: #667eea; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
      .card { background: white; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 2px solid #ddd; border-radius: 8px; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; margin-top: 10px; }
      .error { color: red; text-align: center; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Login Profes 🔒</h2>
            <form method="post">
                <input name="usuario" placeholder="Usuario" required>
                <input name="clave" type="password" placeholder="Contraseña" required>
                <button type="submit">Entrar</button>
            </form>
            <div class="error">%s</div>
        </div>
    </body>
    </html>
    ''' % error

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'logueado' not in session:
        return redirect(url_for('login'))
    
    resultado = ''
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            n1 = float(request.form['n1'])
            n2 = float(request.form['n2'])
            n3 = float(request.form['n3'])
            promedio = (n1 + n2 + n3) / 3
            resultado = "Promedio: %.1f" % promedio
            
            conn = sqlite3.connect('notas.db')
            c = conn.cursor()
            c.execute('INSERT INTO registros (nombre, n1, n2, n3, promedio, fecha) VALUES (?,?,?,?,?,?)',
                     (nombre, n1, n2, n3, promedio, datetime.now().strftime('%d/%m/%Y %H:%M')))
            conn.commit()
            conn.close()
        except:
            resultado = "Error: Completa todos los campos"
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calculadora</title>
        <style>
        body { font-family: Arial; background: #667eea; padding: 20px; }
      .card { background: white; padding: 30px; border-radius: 12px; max-width: 600px; margin: 0 auto; }
      .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 2px solid #ddd; border-radius: 8px; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; margin-top: 10px; }
      .btn-logout { width: auto; padding: 8px 16px; background: #ff4757; }
      .resultado { margin-top: 20px; padding: 15px; background: #2ed573; color: white; border-radius: 8px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h2>Calculadora de Notas 📊</h2>
                <a href="/logout"><button class="btn-logout">Cerrar Sesión</button></a>
            </div>
            <form method="post">
                <input name="nombre" placeholder="Nombre del alumno" required>
                <input name="n1" type="number" step="0.1" placeholder="Nota 1" required>
                <input name="n2" type="number" step="0.1" placeholder="Nota 2" required>
                <input name="n3" type="number" step="0.1" placeholder="Nota 3" required>
                <button type="submit">Calcular y Guardar</button>
            </form>
            %s
            <p style="text-align:center; margin-top:20px; font-size:12px;">Nivel 4: Login Seguro</p>
        </div>
    </body>
    </html>
    ''' % ('<div class="resultado">'+resultado+'</div>' if resultado else '')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
