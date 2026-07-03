from flask import Flask, request, make_response, session, redirect, url_for
from xhtml2pdf import pisa
from io import BytesIO
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'santos-leon-yaounde-2026-secreto'

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

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logueado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def crear_pdf(nombre, n1, n2, n3, promedio):
    color_clase = 'verde' if promedio >= 10 else 'rojo'
    html = '''
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; padding: 40px; }
            h1 { color: #667eea; text-align: center; }
           .card { border: 2px solid #667eea; padding: 20px; border-radius: 10px; }
           .verde { background: #2ed573; color: white; padding: 15px; text-align: center; font-size: 24px; }
           .rojo { background: #ff4757; color: white; padding: 15px; text-align: center; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1>Reporte de Notas 📊</h1>
        <div class="card">
            <p><b>Alumno:</b> %s</p>
            <p><b>Nota 1:</b> %.1f</p>
            <p><b>Nota 2:</b> %.1f</p>
            <p><b>Nota 3:</b> %.1f</p>
            <div class="%s">
                <b>Promedio Final: %.1f</b>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 12px;">
                Generado desde Yaoundé 🇨🇲 - %s
            </p>
        </div>
    </body>
    </html>
    ''' % (nombre, n1, n2, n3, color_clase, promedio, datetime.now().strftime('%d/%m/%Y %H:%M'))
    
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
    
    mostrar_error = 'block' if error else 'none'
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Notas Pro+</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;
        }
       .card {
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
            padding: 40px 30px; border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%; max-width: 400px; animation: slideUp 0.5s ease;
        }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        h2 { text-align: center; color: #333; margin-bottom: 30px; font-weight: 700; font-size: 26px; }
        input {
            width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0;
            border-radius: 12px; font-size: 16px; transition: all 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; transform: scale(1.02); }
        button {
            width: 100%; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 600;
            cursor: pointer; margin-top: 10px; transition: all 0.3s;
        }
        button:active { transform: scale(0.98); }
       .error {
            margin-top: 15px; padding: 15px; background: #ff4757; color: white;
            border-radius: 12px; text-align: center; font-weight: 600; display: %s;
        }
       .footer { text-align: center; margin-top: 25px; font-size: 12px; color: #666; }
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
            <div class="error">%s</div>
            <p class="footer">Calculadora de Notas Pro+ | Nivel 4</p>
        </div>
    </body>
    </html>
    ''' % (mostrar_error, error)

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
                resultado = "Tu promedio es: %.1f" % promedio
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
                    response.headers['Content-Disposition'] = 'attachment; filename=notas_%s.pdf' % nombre
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
            filas += '''
            <tr>
                <td>%s</td>
                <td>%.1f</td>
                <td>%.1f</td>
                <td>%.1f</td>
                <td style="background:%s; color:white; font-weight:bold;">%.1f</td>
                <td>%s</td>
            </tr>''' % (r[1], r[2], r[3], r[4], color_fila, r[5], r[6])
        tabla_historial = '''
        <div class="historial">
            <h3>Últimos 10 registros 📋</h3>
            <table>
                <tr><th>Alumno</th><th>N1</th><th>N2</th><th>N3</th><th>Prom</th><th>Fecha</th></tr>
                %s
            </table>
            <form method="post">
                <button type="submit" name="borrar" class="btn-borrar">Borrar Historial 🗑️</button>
            </form>
        </div>''' % filas
    
    mostrar_resultado = 'block' if resultado else 'none'
    mostrar_pdf = 'block' if resultado else 'none'
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calculadora de Notas Pro+</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
       .container { max-width: 900px; margin: 0 auto; }
       .card {
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
            padding: 40px 30px; border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 20px; animation: slideUp 0.5s ease;
        }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
       .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        h2 { color: #333; font-weight: 700; font-size: 26px; }
       .btn-logout {
            width: auto; padding: 10px 20px; font-size: 14px;
            background: linear-gradient(135deg, #ff4757 0%, #ff6348 100%);
        }
        h3 { text-align: center; color: #333; margin-bottom: 20px; font-weight: 600; }
        input {
            width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0;
            border-radius: 12px; font-size: 16px; transition: all 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; transform: scale(1.02); }
        button {
            width: 100%; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 600;
            cursor: pointer; margin-top: 10px; transition: all 0.3s;
        }
        button:active { transform: scale(0.98); }
       .btn-pdf {
            background: linear-gradient(135deg, #2ed573 0%, #17c0eb 100%);
            display: %s;
        }
       .btn-borrar {
            background: linear-gradient(135deg, #ff4757 0%, #ff6348 100%);
            margin-top: 15px;
        }
       .resultado {
            margin-top: 25px; padding: 20px; background: %s; color: white;
            border-radius: 12px; text-align: center; font-size: 20px; font-weight: 700;
            animation: pop 0.4s ease; display: %s;
        }
        @keyframes pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
       .historial { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
        th, td { padding: 12px 8px; text-align: center; border-bottom: 1px solid #e0e0e0; }
        th { background: #667eea; color: white; font-weight: 600; }
        tr:hover { background: #f5f5f5; }
       .footer { text-align: center; margin-top: 25px; font-size: 12px; color: #666; }
        @media (max-width: 600px) {
            table { font-size: 12px; }
            th, td { padding: 8px 4px; }
           .header { flex-direction: column; gap: 15px; }
        }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="header">
                    <h2>Calculadora de Notas Pro+ 📊</h2>
                    <a href="/logout"><button class="btn-logout">Cerrar Sesión</button></a>
                </div>
                <form method="post">
                    <input name="nombre" placeholder="Nombre del alumno" type="text" value="%s" required>
                    <input name="n1" placeholder="Nota 1" type="number" step="0.1" value="%s" required>
                    <input name="n2" placeholder="Nota 2" type="number" step="0.1" value="%s" required>
                    <input name="n3" placeholder="Nota 3" type="number" step="0.1" value="%s" required>
                    <button type="submit">Calcular y Guardar 💾</button>
                    <button type="submit" name="pdf" value="1" class="btn-pdf">Descargar PDF 📄</button>
                </form>
                <div class="resultado">%s</div>
                <p class="footer">Hecho a las 5AM en Yaoundé 🇨🇲 | Nivel 4: Login Seguro</p>
            </div>
            %s
        </div>
    </body>
    </html>
    ''' % (mostrar_pdf, color, mostrar_resultado, nombre, n1 if n1 else '', n2 if n2 else '', n3 if n3 else '', resultado, tabla_historial)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
