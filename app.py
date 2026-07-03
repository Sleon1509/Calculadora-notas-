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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 40px 30px;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    width: 100%;
    max-width: 400px;
    animation: slideUp 0.5s ease;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
    font-weight: 700;
    font-size: 28px;
}

input {
    width: 100%;
    padding: 15px;
    margin: 12px 0;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    font-size: 16px;
    transition: all 0.3s;
    font-family: 'Poppins', sans-serif;
}

input:focus {
    outline: none;
    border-color: #667eea;
    transform: scale(1.02);
}

button {
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
    font-family: 'Poppins', sans-serif;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

button:active {
    transform: translateY(0);
}

.resultado {
    margin-top: 25px;
    padding: 20px;
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border-radius: 12px;
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    animation: pop 0.4s ease;
}

@keyframes pop {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.footer {
    text-align: center;
    margin-top: 25px;
    font-size: 12px;
    color: #666;
}
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
