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

# Programar la ejecución de lector.py cada x segundos 
schedule.every(10).seconds.do(run_lector)

@app.route('/', methods=['GET', 'POST'])
def home():
    conn = sqlite3.connect('base_de_datos.db')
    c = conn.cursor()

    search_query = request.args.get('search')

    if search_query:
        c.execute('''
        SELECT DISTINCT * FROM recipe 
        WHERE (cedula LIKE ? OR nombres LIKE ? OR apellidos LIKE ? OR producto LIKE ?) AND (en_proceso = FALSE AND cotizado_parcial = FALSE AND cotizado_total = FALSE AND facturado_parcial = FALSE AND facturado_total = FALSE)
    ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute('SELECT DISTINCT * FROM recipe WHERE en_proceso = FALSE AND cotizado_parcial = FALSE AND cotizado_total = FALSE AND facturado_parcial = FALSE AND facturado_total = FALSE')

    recipes = c.fetchall()

    conn.close()

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
    
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    conn = sqlite3.connect('base_de_datos.db')
    c = conn.cursor()
    # Asumir que 'value' ya es booleano (true o false) y usarlo directamente
    c.execute(f'UPDATE recipe SET {data["status"]} = ? WHERE id = ?', (data['value'], data['id']))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/filter', methods=['GET'])
def filter():
    filter_status = request.args.get('status')
    conn = sqlite3.connect('base_de_datos.db')  
    c = conn.cursor()
    if filter_status is not None:
        filter_status = filter_status.lower()
        if filter_status in ['en_proceso', 'cotizado_parcial', 'cotizado_total', 'facturado_parcial', 'facturado_total']:
            c.execute(f'SELECT * FROM recipe WHERE {filter_status} = 1')
        elif filter_status == 'todos':
            c.execute('SELECT * FROM recipe')
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