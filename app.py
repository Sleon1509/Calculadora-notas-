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
