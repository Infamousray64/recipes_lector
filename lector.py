import xml.etree.ElementTree as ET
import sqlite3
import os

# Conectar a la base de datos SQLite
conn = sqlite3.connect('base_de_datos.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS recipe (
        fecha TEXT,
        medicotratante TEXT,
        especialidad TEXT,
        responsablepago TEXT,
        nombres TEXT,
        apellidos TEXT,
        nacionalidad TEXT,
        cedula TEXT,
        telefonos TEXT,
        sms TEXT,
        correo TEXT,
        producto TEXT,
        principio_activo TEXT
    )
''')

# Directorio donde se encuentran los archivos XML
dir_name = 'recipes/'

# Iterar sobre cada archivo en el directorio
for filename in os.listdir(dir_name):
    if filename.endswith('.xml'):
        # Parsear el archivo XML
        tree = ET.parse(os.path.join(dir_name, filename))
        root = tree.getroot()

        # Extraer los campos del archivo XML
        fecha = root.find('fecha').text
        medicotratante = root.find('medicotratante').text
        especialidad = root.find('especialidad').text
        responsablepago = root.find('responsablepago').text
        nombres = root.find('paciente/nombres').text
        apellidos = root.find('paciente/apellidos').text
        nacionalidad = root.find('paciente/nacionalidad').text
        cedula = root.find('paciente/cedula').text
        telefonos = root.find('paciente/telefonos').text
        sms = root.find('paciente/sms').text
        correo = root.find('paciente/correo').text
        producto = root.find('medicamentos/medicamento/producto').text
        principio_activo = root.find('medicamentos/medicamento/principio-activo').text

        c.execute('''
            SELECT * FROM recipe WHERE fecha = ? AND medicotratante = ? AND especialidad = ? AND responsablepago = ? AND nombres = ? AND apellidos = ? AND nacionalidad = ? AND cedula = ? AND telefonos = ? AND sms = ? AND correo = ? AND producto = ? AND principio_activo = ?
        ''', (fecha, medicotratante, especialidad, responsablepago, nombres, apellidos, nacionalidad, cedula, telefonos, sms, correo, producto, principio_activo))

        if c.fetchone() is None:
            c.execute('''
            INSERT INTO recipe VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, medicotratante, especialidad, responsablepago, nombres, apellidos, nacionalidad, cedula, telefonos, sms, correo, producto, principio_activo))
# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()