from flask import Flask, request, make_response, session, redirect, url_for
from xhtml2pdf import pisa
from io import BytesIO
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'santos-leon-dev-yaounde-2026' # Cambia esto por algo secreto

# Usuario y clave del profe. CÁMBIALOS
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

# Decorador para proteger rutas
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logueado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def crear_pdf(nombre, n1, n2, n3, promedio):
    html = f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial; padding: 40px; }}
            h1 {{ color: #667eea; text-align: center; }}
          .card {{ border: 2px solid #667eea; padding: 20px; border-radius: 10px; }}
          .verde {{ background: #2ed573; color: white; padding: 15px; text-align: center; font-size: 24px; }}
          .rojo {{ background: #ff4757; color: white; padding: 15px; text-align: center; font-size: 24px; }}
        </style>
    </head>
    <body>
        <h1>Reporte de Notas 📊</h1>
        <div class="card">
            <p><b>Alumno:</b> {nombre}</p>
            <p><b>Nota 1:</b> {n1}</p>
            <p><b>Nota 2:</b> {n2}</p>
            <p><b>Nota 3:</b> {n3}</p>
            <div class="{'verde' if promedio >= 10 else 'rojo'}">
                <b>Promedio Final: {promedio:.1f}</b>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 12px;">
                Generado desde Yaoundé 🇨🇲 - {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
    </body>
    </html>
    '''
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf)
    pdf.seek(0)
    return pdf

def obtener_historial():
    conn = sqlite3.connect('notas.db')
    c = conn.cursor()
    c.execute('SELECT * FROM registros ORDER BY id DESC LIMIT 10')
    datos = c.fetchall()
    conn.close()
    return datos

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['clave'] == CLAVE:
            session['logueado'] = True
            return redirect(url_for('home'))
        else:
            error = 'Usuario o clave incorrectos'
    
    return f'''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Notas Pro+</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
      .card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 40px 30px;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
            animation: slideUp 0.5s ease;
        }}
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h2 {{ text-align: center; color: #333; margin-bottom: 30px; font-weight: 700; font-size: 26px; }}
        input {{
            width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0;
            border-radius: 12px; font-size: 16px; transition: all 0.3s;
        }}
        input:focus {{ outline: none; border-color: #667eea; transform: scale(1.02); }}
        button {{
            width: 100%; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 600;
            cursor: pointer; margin-top: 10px; transition: all 0.3s;
        }}
        button:active {{ transform: scale(0.98); }}
      .error {{
            margin-top: 15px; padding: 15px; background: #ff4757; color: white;
            border-radius: 12px; text-align: center; font-weight: 600;
            display: {'block' if error else 'none'};
        }}
      .footer {{ text-align: center; margin-top: 25px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Login Profes 🔒</h2>
            <form method="post">
                <input name="usuario" placeholder="Usuario" type="text" required>
                <input name="clave" placeholder="Contraseña" type="password" required>
                <button type="submit">Entrar</button>
            </form>
            <div class="error">{error}</div>
            <p class="footer">Calculadora de Notas Pro+ | Nivel 4</p>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.pop('logueado', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_requerido
def home():
    resultado = ''
    color = 'white'
    nombre = ''
    n1 = n2 = n3 = 0
    promedio = 0
    
    if request.method == 'POST':
        if 'borrar' in request.form:
            conn = sqlite3.connect('notas.db')
            c = conn.cursor()
            c.execute('DELETE FROM registros')
            conn.commit()
            conn.close()
        else:
            try:
                nombre = request.form['nombre']
                n1 = float(request.form['n1'])
                n2 = float(request.form['n2'])
                n3 = float(request.form['n3'])
                promedio = (n1 + n2 + n3) / 3
                resultado = f"Tu promedio es: {promedio:.1f}"
                color = '#ff4757' if promedio < 10 else '#2ed573'
                
                conn = sqlite3.connect('notas.db')
                c = conn.cursor()
                c.execute('INSERT INTO registros (nombre, n1, n2, n3, promedio, fecha) VALUES (?,?,?,?,?,?)',
                         (nombre, n1, n2, n3, promedio, datetime.now().strftime('%d/%m/%Y %H:%M')))
                conn.commit()
                conn.close()
                
                if 'pdf' in request.form:
                    pdf = crear_pdf(nombre, n1, n2, n3, promedio)
                    response = make_response(pdf.read())
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = f'attachment; filename=notas_{nombre}.pdf'
                    return response
                    
            except:
                resultado = "Error: Completa todos los campos"
                color = '#ff4757'
    
    historial = obtener_historial()
    tabla_historial = ''
    if historial:
        filas = ''
        for r in historial:
            color_fila = '#2ed573' if r[5] >= 10 else '#ff4757'
            filas += f'''
            <tr>
                <td>{r[1]}</td>
                <td>{r[2]}</td>
                <td>{r[3]}</td>
                <td>{r[4]}</td>
                <td style="background:{color_fila}; color:white; font-weight:bold;">{r[5]:.1f}</td>
                <td>{r[6]}</td>
            </tr>'''
        tabla_historial = f'''
        <div class="historial">
            <h3>Últimos 10 registros 📋</h3>
            <table>
                <tr><th>Alumno</th><th>N1</th><th>N2</th><th>N3</th><th>Prom</th><th>Fecha</th></tr>
                {filas}
            </table
