import sqlite3

# Conectar a la base de datos SQLite
conn = sqlite3.connect('base_de_datos.db')
c = conn.cursor()

# Consultar todos los datos de la tabla 'recipe'
c.execute('SELECT * FROM recipe')

# Imprimir todos los resultados
for row in c.fetchall():
    print(row)

# Cerrar la conexión
conn.close()