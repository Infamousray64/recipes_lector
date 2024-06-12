from flask import Flask, render_template, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
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
    
    # Convertir el valor booleano a un entero
    value_int = 1 if data['value'] else 0
    
    # Establecer la zona horaria deseada como UTC -4
    utc_minus_4 = timezone(timedelta(hours=-4))
    
    # Formatear clickedTime para que coincida con el formato de tu base de datos
    if 'clickedTime' in data:
        # Asumiendo que clickedTime viene en el formato ISO 8601 y necesita conversión a UTC -4
        clicked_time = datetime.fromisoformat(data['clickedTime'].rstrip('Z')).replace(tzinfo=timezone.utc).astimezone(utc_minus_4).strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Obtener la hora actual ajustada a UTC -4
        clicked_time = datetime.now(utc_minus_4).strftime('%Y-%m-%d %H:%M:%S')
    
    # Asumir que tienes una columna llamada '{status}_time' para almacenar la hora del clic
    status_time_column = f"{data['status']}_time"
    
    # Preparar la consulta SQL para evitar inyecciones SQL
    sql = f'UPDATE recipe SET {data["status"]} = ?, {status_time_column} = ? WHERE id = ?'
    c.execute(sql, (value_int, clicked_time, data['id']))
    
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