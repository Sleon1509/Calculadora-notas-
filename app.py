from flask import Flask, request, session, redirect, url_for, make_response
from xhtml2pdf import pisa
from io import BytesIO
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-yaounde-2026')

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

def crear_pdf(nombre, n1, n2, n3, promedio):
    color = '#2ed573' if promedio >= 10 else '#ff4757'
    estado = 'APROBADO' if promedio >= 10 else 'REPROBADO'
    
    html = '''
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial; padding: 40px; }}
            h1 {{ color: #667eea; text-align: center; }}
           .card {{ border: 2px solid #667eea; padding: 20px; border-radius: 10px; }}
           .promedio {{ background: {color}; color: white; padding: 15px; text-align: center; font-size: 24px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <h1>Reporte de Notas 📊</h1>
        <div class="card">
            <p><b>Alumno:</b> {nombre}</p>
            <p><b>Nota 1:</b> {n1:.1f}</p>
            <p><b>Nota 2:</b> {n2:.1f}</p>
            <p><b>Nota 3:</b> {n3:.1f}</p>
            <div class="promedio">
                <b>Promedio: {promedio:.1f} - {estado}</b>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 12px;">
                Generado desde Yaoundé 🇨🇲 - {fecha}
            </p>
        </div>
    </body>
    </html>
    '''.format(nombre=nombre, n1=n1, n2=n2, n3=n3, promedio=promedio, estado=estado, color=color, fecha=datetime.now().strftime('%d/%m/%Y %H:%M'))
    
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
        error = 'Usuario o clave incorrectos'
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
        body {{ font-family: Arial; background: #667eea; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
       .card {{ background: white; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; }}
        input {{ width: 100%; padding: 12px; margin: 8px 0; border: 2px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
        button {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; margin-top: 10px; font-size: 16px; }}
       .error {{ color: red; text-align: center; margin-top: 10px; }}
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
            <div class="error">{}</div>
        </div>
    </body>
    </html>
    '''.format(error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'logueado' not in session:
        return redirect(url_for('login'))
    
    resultado = ''
    color_resultado = '#2ed573'
    mostrar_pdf = 'none'
    nombre = n1 = n2 = n3 = promedio = 0
    
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
                
                if n1 < 0 or n1 > 20 or n2 < 0 or n2 > 20 or n3 < 0 or n3 > 20:
                    resultado = "Error: Las notas deben ser entre 0 y 20"
                    color_resultado = '#ff4757'
                else:
                    promedio = (n1 + n2 + n3) / 3
                    estado = 'APROBADO' if promedio >= 10 else 'REPROBADO'
                    resultado = "Promedio: {:.1f} - {}".format(promedio, estado)
                    color_resultado = '#2ed573' if promedio >= 10 else '#ff4757'
                    mostrar_pdf = 'block'
                    
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
                        response.headers['Content-Disposition'] = 'attachment; filename=notas_{}.pdf'.format(nombre.replace(' ', '_'))
                        return response
                        
            except:
                resultado = "Error: Completa todos los campos con números"
                color_resultado = '#ff4757'
    
    historial = obtener_historial()
    tabla = ''
    if historial:
        filas = ''
        for r in historial:
            color_fila = '#2ed573' if r[5] >= 10 else '#ff4757'
            filas += '<tr><td>{}</td><td>{:.1f}</td><td>{:.1f}</td><td>{:.1f}</td><td style="background:{};color:white;font-weight:bold;">{:.1f}</td><td>{}</td></tr>'.format(r[1], r[2], r[3], r[4], color_fila, r[5], r[6])
        
        tabla = '''
        <div style="margin-top:20px;">
            <h3>Últimos 10 registros 📋</h3>
            <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:14px;">
                <tr style="background:#667eea;color:white;"><th>Alumno</th><th>N1</th><th>N2</th><th>N3</th><th>Prom</th><th>Fecha</th></tr>
                {}
            </table>
            <form method="post">
                <button type="submit" name="borrar" style="background:#ff4757;margin-top:15px;">Borrar Historial 🗑️</button>
            </form>
        </div>
        '''.format(filas)
    
    return '''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calculadora de Notas Pro+</title>
        <style>
        body {{ font-family: Arial; background: #667eea; padding: 20px; margin: 0; }}
       .container {{ max-width: 900px; margin: 0 auto; }}
       .card {{ background: white; padding: 30px; border-radius
