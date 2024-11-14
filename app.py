from flask import (Flask, render_template_string, render_template, url_for, request, redirect,
                   session, flash, Response, url_for, send_file, jsonify)
import cv2
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64
import textwrap
import google.generativeai as genai
from markupsafe import Markup
from fpdf import FPDF
from nicegui import ui

from scipy.ndimage import label
from ejercicios import  ejercicio_sentadillas



usuarios = {
    "usuario1": {
        "correo": "usuario1@gmail.com",
        "clave": "123",
        "rol": "vendedor"
    },
    "usuario2": {
        "correo": "usuario2@gmail.com",
        "clave": "456",
        "rol": "vendedor"
    },
    "usuario3": {
        "correo": "usuario3@gmail.com",
        "clave": "789",
        "rol": "gerente"
    }
}


app = Flask(__name__)
app.secret_key = 'cochabamba'

#------------------------------------- PARTE DEL CHATBOT-----------------------------

genai.configure(api_key="codigo-api")
# Define el modelo
model = genai.GenerativeModel("gemini-1.5-flash")

def to_markdown(text):
    """Convierte el texto en formato Markdown."""
    text = text.replace('•', '  *')
    return Markup(textwrap.indent(text, '> ', predicate=lambda _: True))

# --------------------------------------- PARTE DE LAS RUTAS --------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/validar_login', methods=['POST',])
def validar_login():
    usuario_formulario = request.form['username']
    clave_formulario = request.form['password']

    if usuario_formulario in usuarios:
        user_data = usuarios[usuario_formulario]
        user_login = user_data
        user_clave = user_data['clave']
        user_rol = user_data['rol']
        if user_clave == clave_formulario:
            session['usuario_logueado'] = usuario_formulario
            session['rol'] = user_rol
            return render_template('index.html')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))  #  usuario inexistente


@app.route('/logout')
def logout():
    session['usuario_logueado'] = None
    flash('¡Logout efectuado exitosamente!')
    return redirect(url_for('home'))


@app.route('/sentadillas')
def sentadillas():
    return ejercicio_sentadillas.detectar_sentadillas()


@app.route('/ejercicios')
def ejercicios():
    return render_template('ejercicios.html')


@app.route('/recetas')
def recetas():
    return  render_template('recetas.html')


@app.route('/registro')
def registro():
    return render_template('registro.html')


@app.route('/planesnutritivos')
def planes_nutritivos():
    return render_template('planes_nutritivos.html')


#@app.route('/reportes')
#def reportes():
#    return  render_template('reportes.html')


@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

#-------------------------------------parte del CHATBOT------------------------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input')
    if user_input:
        try:
            response = model.generate_content(prompt=user_input)  # Intentamos usar el parámetro 'prompt'

            response_text = response.get('content', 'No se generó contenido.')

            return jsonify({'response': to_markdown(response_text)})
        except Exception as e:
            return jsonify({'response': f'Error al generar respuesta: {str(e)}'})
    return jsonify({'response': 'Error: no se recibió entrada.'})



@app.route('/')
def index():
    return render_template('footer.html')


#--------------------------------------------------------------------------------------------------
#------------------------------------ PARTE DE LA CALCULADORA --------------------------------------
@app.route('/calculadora', methods=['GET', 'POST'])
def imc_calculator():
    if request.method == 'POST':
        try:
            estatura = float(request.form['tamaño'])
            peso = float(request.form['peso'])
            imc = peso / (estatura ** 2)

            # Generar el gráfico de niveles de IMC
            img = io.BytesIO()

            # Definimos los niveles de IMC y las categorías
            labels = [
                'Delgadez severa', 'Delgadez moderada', 'Bajo peso', 'Normal',
                'Sobrepeso', 'Obesidad clase I', 'Obesidad clase II', 'Obesidad clase III'
            ]
            levels = [16, 17, 18.5, 24.9, 29.9, 34.9, 39.9, 50]
            colors = ['#023047', '#219ebc', '#8338ec', '#06d6a0', '#FFD700', '#FF8C00', '#FF4500', '#8B0000']

            plt.figure(figsize=(7, 4))
            plt.bar(labels, levels, color=colors)
            plt.axhline(imc, color='black', linestyle='--', label=f'Tu Indice de Masa Corporal: {imc:.2f}')
            plt.legend()

            plt.xticks(rotation=45, ha='right')
            plt.xlabel("Categorías de IMC")
            plt.ylabel("IMC")
            plt.tight_layout()

            # Convertimos la imagen en base64 para mostrar en el HTML
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            return render_template('calculadora.html', imc=imc, plot_url=plot_url)
        except ValueError:
            return redirect(url_for('imc_calculator'))

    return render_template('calculadora.html')


#------------------------------------- PARTE DE REPORTES ----------------------------------------------
@app.route('/reportes')
def reportes():
    usuarios = [
        {'nombre': 'Juan Pérez', 'edad': 28, 'peso': 70, 'estatura': 1.75, 'sexo': 'M', 'imc': 22.86, 'calorias': 2500},
        {'nombre': 'Ana Gómez', 'edad': 32, 'peso': 60, 'estatura': 1.68, 'sexo': 'F', 'imc': 21.26, 'calorias': 2200},
        {'nombre': 'Luis Rodríguez', 'edad': 45, 'peso': 85, 'estatura': 1.78, 'sexo': 'M', 'imc': 26.83, 'calorias': 2800},
        {'nombre': 'María López', 'edad': 29, 'peso': 55, 'estatura': 1.65, 'sexo': 'F', 'imc': 20.2, 'calorias': 2100},
        {'nombre': 'Carlos Díaz', 'edad': 35, 'peso': 95, 'estatura': 1.80, 'sexo': 'M', 'imc': 29.32, 'calorias': 3000},
    ]

    return render_template('reportes.html', usuarios=usuarios)


@app.route('/generar_pdf')
def generar_pdf():
    usuarios = [
        {'nombre': 'Juan Pérez', 'edad': 28, 'peso': 70, 'estatura': 1.75, 'sexo': 'M', 'imc': 22.86, 'calorias': 2500},
        {'nombre': 'Ana Gómez', 'edad': 32, 'peso': 60, 'estatura': 1.68, 'sexo': 'F', 'imc': 21.26, 'calorias': 2200},
        {'nombre': 'Luis Rodríguez', 'edad': 45, 'peso': 85, 'estatura': 1.78, 'sexo': 'M', 'imc': 26.83, 'calorias': 2800},
        {'nombre': 'María López', 'edad': 29, 'peso': 55, 'estatura': 1.65, 'sexo': 'F', 'imc': 20.2, 'calorias': 2100},
        {'nombre': 'Carlos Díaz', 'edad': 35, 'peso': 95, 'estatura': 1.80, 'sexo': 'M', 'imc': 29.32, 'calorias': 3000},
    ]

    # Crear el PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Reporte de Usuarios", ln=True, align='C')

    pdf.set_font("Arial", "B", 10)
    encabezados = ["Nombre", "Edad", "Peso (kg)", "Estatura (m)", "Sexo", "IMC", "Calorías"]
    for encabezado in encabezados:
        pdf.cell(30, 10, encabezado, border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for usuario in usuarios:
        pdf.cell(30, 10, usuario['nombre'], border=1)
        pdf.cell(30, 10, str(usuario['edad']), border=1)
        pdf.cell(30, 10, str(usuario['peso']), border=1)
        pdf.cell(30, 10, f"{usuario['estatura']:.2f}", border=1)
        pdf.cell(30, 10, usuario['sexo'], border=1)
        pdf.cell(30, 10, f"{usuario['imc']:.2f}", border=1)
        pdf.cell(30, 10, str(usuario['calorias']), border=1)
        pdf.ln()

    # Guardar el contenido en BytesIO
    output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    output.write(pdf_bytes)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="reporte_usuarios.pdf", mimetype='application/pdf')



#--------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
