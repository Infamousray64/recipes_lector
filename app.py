from flask import Flask, render_template, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from flask import Flask, send_file
from io import BytesIO
from flask import Flask, request, make_response
from flask_socketio import SocketIO
from openpyxl import Workbook
import openpyxl
import pandas as pd
import sqlite3
import schedule
import time
import subprocess
import os

app = Flask(__name__)
socketio = SocketIO(app)

def run_lector():
    # Ejecutar lector.py
    subprocess.run(["python", "lector.py"])

# Programar la ejecución de lector.py cada x segundos 
schedule.every(10).seconds.do(run_lector)


@app.route('/', methods=['GET', 'POST'])
def home():
    # Obtener la fecha actual en el formato dd/mm/aaaa
    today_date = datetime.now().strftime('%d/%m/%Y')

    conn = sqlite3.connect('base_de_datos.db')
    c = conn.cursor()

    search_query = request.args.get('search')

    if search_query:
        # Filtrar también por la fecha actual junto con la búsqueda y dar prioridad a los registros con estado_actual NULL
        c.execute('''
        SELECT DISTINCT * FROM recipe 
        WHERE (cedula LIKE ? OR nombres LIKE ? OR apellidos LIKE ? OR producto LIKE ?) 
        AND fecha = ?
        ORDER BY CASE WHEN estado_actual IS NULL THEN 0 ELSE 1 END, 
        SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2) DESC
        ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', today_date))
    else:
        # Filtrar los resultados para mostrar solo los de la fecha actual y dar prioridad a los registros con estado_actual NULL
        c.execute('''
        SELECT DISTINCT * FROM recipe 
        WHERE fecha = ?
        ORDER BY CASE WHEN estado_actual IS NULL THEN 0 ELSE 1 END, 
        SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2) DESC
        ''', (today_date,))
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
    try:
        estatus = request.args.get('estatus', 'todos')  # Si no se proporciona, usar 'todos'
        mes = request.args.get('mes', default=None)
        ano = request.args.get('ano', default=None)

        # Si mes o ano son cadenas vacías, tratarlos como None
        mes = None if mes == '' else mes
        ano = None if ano == '' else ano

        query, params = build_query(estatus, mes, ano)

        with sqlite3.connect('base_de_datos.db') as conn:
            df = pd.read_sql_query(query, conn, params=params)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return send_file(output, as_attachment=True, download_name="recipes.xls", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return str(e), 500

def build_query(estatus, mes, ano):
    # Si mes y ano no se proporcionan, seleccionar todos los registros sin importar el estatus
    if not mes and not ano:
        return "SELECT * FROM recipe", ()
    else:
        if estatus is None or estatus == 'todos':
            if mes and ano:
                # Ajuste para manejar fechas en formato dd/mm/aaaa
                return "SELECT * FROM recipe WHERE SUBSTR(fecha, 4, 2) = ? AND SUBSTR(fecha, 7, 4) = ?", (mes, ano)
            else:
                return "SELECT * FROM recipe", ()
        else:
            if mes and ano:
                # Ajuste para manejar fechas en formato dd/mm/aaaa
                return "SELECT * FROM recipe WHERE estado_actual = ? AND SUBSTR(fecha, 4, 2) = ? AND SUBSTR(fecha, 7, 4) = ?", (estatus, mes, ano)
            else:
                return "SELECT * FROM recipe WHERE estado_actual = ?", (estatus,)
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