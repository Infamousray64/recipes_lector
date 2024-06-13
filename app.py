from flask import Flask, render_template, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from flask import Flask, send_file
from io import BytesIO
from flask import Flask, request, make_response
import pandas as pd
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
        WHERE (cedula LIKE ? OR nombres LIKE ? OR apellidos LIKE ? OR producto LIKE ?) 
        ORDER BY SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2) DESC
        ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute('''SELECT DISTINCT * FROM recipe ORDER BY SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2) DESC''')
    recipes = c.fetchall()

    conn.close()

    return render_template('home.html', recipes=recipes)
    
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
        clicked_time = datetime.fromisoformat(data['clickedTime'].rstrip('Z')).replace(tzinfo=timezone.utc).astimezone(utc_minus_4).strftime('%Y-%m-%d %H:%M:%S')
    else:
        clicked_time = datetime.now(utc_minus_4).strftime('%Y-%m-%d %H:%M:%S')
    
    status_time_column = f"{data['status']}_time"
    
    # Actualizar el estado y la hora del estado
    sql = f'UPDATE recipe SET {data["status"]} = ?, {status_time_column} = ?, estado_actual = ? WHERE id = ?'
    c.execute(sql, (value_int, clicked_time, data['status'], data['id']))
    
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/filter', methods=['GET'])
def filter():
    filter_status = request.args.get('status')
    conn = sqlite3.connect('base_de_datos.db')  
    c = conn.cursor()
    # Ordenamiento por fecha más reciente
    order_by = "ORDER BY SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2) DESC"
    if filter_status:
        filter_status = filter_status.lower().replace(" ", "_")
        if filter_status == 'todos':
            query = f'SELECT * FROM recipe {order_by}'
        else:
            query = f'SELECT * FROM recipe WHERE estado_actual = ? {order_by}'
            c.execute(query, (filter_status,))
    else:
        query = f'SELECT * FROM recipe {order_by}'
    # Ejecutar la consulta para el caso 'todos'
    if filter_status == 'todos' or not filter_status:
        c.execute(query)
    recipes = c.fetchall()
    conn.close()
    return render_template('home.html', recipes=recipes)

@app.route('/download')
def download_file():
    estatus = request.args.get('estatus', None)  # Obtener el estatus de los parámetros de la URL
    conn = sqlite3.connect('base_de_datos.db')

    # Preparar la consulta SQL. Si estatus es None o 'todos', selecciona todo. De lo contrario, filtra por estado_actual.
    if estatus is None or estatus == 'todos':
        query = "SELECT * FROM recipe"
    else:
        query = "SELECT * FROM recipe WHERE estado_actual = ?"

    # Ejecutar la consulta y cargar los resultados en un DataFrame de pandas
    if estatus is None or estatus == 'todos':
        df = pd.read_sql_query(query, conn)
    else:
        df = pd.read_sql_query(query, conn, params=(estatus,))

    conn.close()

    # Generar el archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    # Enviar el archivo Excel al usuario
    return send_file(output, as_attachment=True, download_name="recipes.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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