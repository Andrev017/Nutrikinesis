from flask import Flask, render_template_string, render_template, url_for, request, redirect, session, flash, Response
import cv2
from flask_sqlalchemy import SQLAlchemy

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
            return redirect(url_for('login'))  #  clave inexistente
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








if __name__ == "__main__":
    app.run(debug=True)