from flask import Flask, render_template, request
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
        # Si se proporcionó una consulta de búsqueda, buscar la cédula en la base de datos
        c.execute('SELECT DISTINCT * FROM recipe WHERE cedula LIKE ?', ('%' + search_query + '%',))
    else:
        # Si no se proporcionó una consulta de búsqueda, seleccionar todas las recetas
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