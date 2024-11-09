import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def load_user_data():
    # Cargar los datos del archivo Excel como DataFrame
    df = pd.read_excel('users.xlsx')
    
    # Crear una columna 'imagen' con el nombre de archivo de la imagen o 'defecto.png' si no existe
    df['imagen'] = df['usuario'].apply(lambda x: f"{x}.png" if os.path.exists(f"static/images/{x}.png") else "defecto.png")
    
    return df  # Devuelve un DataFrame, no un diccionario

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['nombre'].strip()  # Elimina espacios en blanco
        contraseña = request.form['contraseña'].strip()
        
        # Cargar el DataFrame y verificar su estructura
        df = load_user_data()
        
        # Convertir las columnas a string y eliminar espacios adicionales
        df['usuario'] = df['usuario'].astype(str).str.strip()
        df['contraseña'] = df['contraseña'].astype(str).str.strip()
        
        # Filtrar el DataFrame para encontrar el usuario
        user = df[(df['usuario'] == usuario) & (df['contraseña'] == contraseña)]
        
        if not user.empty:
            session['usuario'] = usuario
            session['nombre'] = user['nombre'].values[0]
            session['tipo_usuario'] = user['tipo_usuario'].values[0]
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Convertir el DataFrame a una lista de diccionarios al pasarlo al template
    users = load_user_data().to_dict(orient='records')
    
    # Calcular el monto total de cuotas pagadas (1s en las columnas de meses)
    total_pagados = sum(
        user['mes_1'] + user['mes_2'] + user['mes_3'] + user['mes_4'] +
        user['mes_5'] + user['mes_6'] + user['mes_7'] + user['mes_8'] +
        user['mes_9'] + user['mes_10'] + user['mes_11'] + user['mes_12']
        for user in users
    )
    cuota = 50000
    recaudado = f"{total_pagados * cuota:,.0f}".replace(",", ".")

    return render_template('home.html', users=users, recaudado=recaudado)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Asegúrate de que el servidor está configurado para ejecutarse en el puerto deseado
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
