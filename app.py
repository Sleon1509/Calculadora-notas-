from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    resultado = ""
    color = "#333"
    if request.method == 'POST':
        try:
            n1 = float(request.form['n1'])
            n2 = float(request.form['n2'])
            n3 = float(request.form['n3'])
            notas = [n for n in [n1,n2,n3] if 0 <= n <= 20]
            if notas:
                prom = sum(notas) / len(notas)
                if prom <= 10: 
                    estado = "Desaprobado"
                    color = "#e74c3c"
                elif prom <= 16: 
                    estado = "Aprobado"
                    color = "#f39c12"
                else: 
                    estado = "Excelente"
                    color = "#27ae60"
                resultado = f"Promedio: {prom:.2f} - {estado}"
            else:
                resultado = "Error: Notas deben ser 0-20"
        except:
            resultado = "Error: Mete números válidos"
            color = "#e74c3c"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; justify-content: center; align-items: center; 
                min-height: 100vh; margin: 0;
            }}
            .card {{
                background: white; padding: 30px; border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                width: 90%; max-width: 400px; text-align: center;
            }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            input {{ 
                width: 100%; padding: 12px; margin: 8px 0; 
                border: 2px solid #ddd; border-radius: 8px; 
                font-size: 16px; box-sizing: border-box;
            }}
            button {{ 
                background: #667eea; color: white; padding: 14px; 
                border: none; border-radius: 8px; width: 100%; 
                font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px;
            }}
            .resultado {{ 
                margin-top: 20px; font-size: 20px; 
                font-weight: bold; color: {color};
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Calculadora de Notas 📊</h2>
            <form method="post">
                <input name="n1" placeholder="Nota 1" type="number" step="0.1" required>
                <input name="n2" placeholder="Nota 2" type="number" step="0.1" required>
                <input name="n3" placeholder="Nota 3" type="number" step="0.1" required>
                <button>Calcular Promedio</button>
            </form>
            <div class="resultado">{resultado}</div>
            <p style="margin-top:20px; font-size:12px; color:#888;">Hecho a las 5AM en Yaoundé 🇨🇲</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
