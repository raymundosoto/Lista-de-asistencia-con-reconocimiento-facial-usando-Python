import os
import datetime
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_data_from_mysql():
    # Conectarse a la base de datos MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="raymundo",
        password="raymundo1234",
        database="asistencia_del_dia"
    )
    cursor = connection.cursor()

    # Obtener la fecha actual en el formato "YYYY-MM-DD"
    current_date = get_current_date()

    # Obtener los datos de la tabla "registro" para la fecha actual
    query = f"SELECT id, fecha, nombre, hora FROM registro WHERE fecha = '{current_date}'"
    cursor.execute(query)
    data = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    connection.close()

    return data


def create_pdf(data):
    # Crear el archivo PDF con el nombre "lista_asistencia_fecha.pdf"
    filename = f"lista_asistencia_{get_current_date()}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Agregar el título en la parte superior del documento as a Flowable object
    title = f"Lista de asistencia del día ({get_current_date()})"
    title_style = getSampleStyleSheet()['Title']
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)

    # Convertir los datos en una lista para la tabla
    data_table = [['ID', 'Fecha', 'Nombre', 'Hora']] + data

    # Crear la tabla
    table = Table(data_table)

    # Estilo de la tabla
    style = TableStyle([
        # ... (tu código de estilo aquí, igual que antes)
    ])
    table.setStyle(style)

    # Agregar la tabla al documento
    elements.append(table)

    # Construir el documento
    doc.build(elements)

if __name__ == "__main__":
    # Obtener los datos de MySQL
    data = get_data_from_mysql()

    # Crear el PDF con los datos de la tabla
    create_pdf(data)

