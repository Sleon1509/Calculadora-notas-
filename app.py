from flask import Flask, request, make_response
from xhtml2pdf import pisa
from io import BytesIO
import os
app = Flask(__name__)

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
                Generado desde Yaoundé 🇨🇲
            </p>
        </div>
    </body>
    </html>
    '''
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf)
    pdf.seek(0)
    return pdf

@app.route('/', methods=['GET', 'POST'])
def home():
    resultado = ''
    color = 'white'
    nombre = ''
    n1 = n2 = n3 = 0
    promedio = 0
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            n1 = float(request.form['n1'])
            n2 = float(request.form['n2'])
            n3 = float(request.form['n3'])
            promedio = (n1 + n2 + n3) / 3
            resultado = f"Tu promedio es: {promedio:.1f}"
            color = '#ff4757' if promedio < 10 else '#2ed573'
            
            if 'pdf' in request.form:
                pdf = crear_pdf(nombre, n1, n2, n3, promedio)
                response = make_response(pdf.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=notas_{nombre}.pdf'
                return response
                
        except:
            resultado = "Error: Completa todos los campos"
            color = '#ff4757'
    
    return f'''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calculadora de Notas Pro</title>
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
        h2 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-weight: 700;
            font-size: 26px;
        }}
        input {{
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #667eea;
            transform: scale(1.02);
        }}
        button {{
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.3s;
        }}
        button:active {{ transform: scale(0.98); }}
        .btn-pdf {{
            background: linear-gradient(135deg, #2ed573 0%, #17c0eb 100%);
            margin-top: 10px;
            display: {'block' if resultado else 'none'};
        }}
        .resultado {{
            margin-top: 25px;
            padding: 20px;
            background: {color};
            color: white;
            border-radius: 12px;
            text-align: center;
            font-size: 20px;
            font-weight: 700;
            animation: pop 0.4s ease;
            display: {'block' if resultado else 'none'};
        }}
        @keyframes pop {{
            0% {{ transform: scale(0.8); opacity: 0; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        .footer {{
            text-align: center;
            margin-top: 25px;
            font-size: 12px;
            color: #666;
        }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Calculadora de Notas Pro 📊</h2>
            <form method="post">
                <input name="nombre" placeholder="Nombre del alumno" type="text" value="{nombre}" required>
                <input name="n1" placeholder="Nota 1" type="number" step="0.1" value="{n1 if n1 else ''}" required>
                <input name="n2" placeholder="Nota 2" type="number" step="0.1" value="{n2 if n2 else ''}" required>
                <input name="n3" placeholder="Nota 3" type="number" step="0.1" value="{n3 if n3 else ''}" required>
                <button type="submit">Calcular Promedio</button>
                <button type="submit" name="pdf" value="1" class="btn-pdf">Descargar PDF 📄</button>
            </form>
            <div class="resultado">{resultado}</div>
            <p class="footer">Hecho a las 5AM en Yaoundé 🇨🇲</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
