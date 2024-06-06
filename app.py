from flask import Flask, render_template, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import schedule
import time
import subprocess
import os

app = Flask(__name__)

def run_lector():
    # Ejecutar lector.py
    subprocess.run(["python", "lector.py"])

# Programar la ejecución de lector.py cada 5 minutos
schedule.every(10).seconds.do(run_lector)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('base_de_datos.db')
    c = conn.cursor()

    search_query = request.args.get('search')

    if search_query:
    # Si se proporcionó una consulta de búsqueda, buscar la cédula, nombres, apellidos y producto en la base de datos
        c.execute('''
        SELECT DISTINCT * FROM recipe 
        WHERE (cedula LIKE ? OR nombres LIKE ? OR apellidos LIKE ? OR producto LIKE ?) 
    ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        # Si no se proporcionó una consulta de búsqueda, seleccionar todas las recipes
        c.execute('SELECT DISTINCT * FROM recipe')

    # Obtener todos los resultados
    recipes = c.fetchall()

    # Cerrar la conexión
    conn.close()

    # Renderizar la plantilla 'home.html' con los datos de las recetas
    return render_template('home.html', recipes=recipes)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and file.filename.endswith('.xml'):
        filename = secure_filename(file.filename)
        file.save(os.path.join('recipes', filename))
        return 'File uploaded successfully'
    
@app.route('/update_procesado', methods=['POST'])
def update_procesado():
    data = request.get_json()
    conn = sqlite3.connect('base_de_datos.db')  # Necesitas abrir la conexión a la base de datos
    c = conn.cursor()
    c.execute('UPDATE recipe SET procesado = ? WHERE id = ?', (data['procesado'], data['id']))
    conn.commit()
    conn.close()  # No olvides cerrar la conexión
    return jsonify(success=True)

@app.route('/filter', methods=['GET'])
def filter():
    filter_status = request.args.get('status')
    conn = sqlite3.connect('base_de_datos.db')  
    c = conn.cursor()
    if filter_status.lower() == 'procesado':
        c.execute('SELECT * FROM recipe WHERE procesado = 1')
    elif filter_status.lower() == 'no procesado':
        c.execute('SELECT * FROM recipe WHERE procesado = 0')
    else:
        c.execute('SELECT * FROM recipe')
    recipes = c.fetchall()
    return render_template('home.html', recipes=recipes)

if __name__ == '__main__':
    # Ejecutar lector.py inmediatamente antes de iniciar la aplicación
    run_lector()
    # Iniciar la aplicación en un hilo separado
    from threading import Thread
    Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False}).start()
    # Iniciar el bucle de programación
    while True:
        schedule.run_pending()
        time.sleep(1)