import face_recognition
import cv2
import numpy as np
import mysql.connector
from datetime import datetime

# Conexion a la base de datos de myqql
db_connection = mysql.connector.connect(
    host="localhost",
    user="raymundo",
    password="raymundo1234",
    database="asistencia_del_dia"
)
db_cursor = db_connection.cursor()

# crear la tabla registro si no existe;
create_table_query = """
CREATE TABLE IF NOT EXISTS registro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    hora TIME NOT NULL
);
"""

db_cursor.execute(create_table_query)

# cargar imagen a reconocer
obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Cargar imagen a reconocer
biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# cargar imagen a reconocer
antonio_image = face_recognition.load_image_file("Antonio_Estrella.jpg")
antonio_face_encoding = face_recognition.face_encodings(antonio_image)[0]

# Cargar imagen a reconocer
scarlett_image = face_recognition.load_image_file("Scarlett.jpg")
scarlett_face_encoding = face_recognition.face_encodings(scarlett_image)[0]


# Create arrays of known face encodings and their names
# Crear arreglos de los encodings de caras conocidas
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    antonio_face_encoding,
    scarlett_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Antonio Estrella",
    "Scarlett Johansson"
]

# Iniciar variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Instancia de la webcam a usar
video_capture = cv2.VideoCapture(0)

while True:
    # Capturar frames
    ret, frame = video_capture.read()


    # procesa una parte de la imagen para hacer más rapido el codigo
    if process_this_frame:
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        #  Convertir a RGB ya que opencv lee BGR
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Encuentra todos los rostros
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Busca matchs en los rostros conocidos
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # o busca un match al mas cercano
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # fecha y hora actual
                now = datetime.now()
                current_date = now.date()
                current_time = now.time()

                # checa si no ha sido registrado el día de hoy
                check_query = "SELECT * FROM registro WHERE nombre = %s AND fecha = %s"
                db_cursor.execute(check_query, (name, current_date))
                result = db_cursor.fetchone()

                if not result:
                    # Inserta el registro en la base  de datos
                    insert_query = "INSERT INTO registro (fecha, nombre, hora) VALUES (%s, %s, %s)"
                    db_cursor.execute(insert_query, (current_date, name, current_time))
                    db_connection.commit()
                else:
                    print(f"{name} Ya ha sido registrado el dia de hoy")

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Muestra los resultados
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Reescala la imagen con el rostro
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Dibuja el rectangulo con el rostro
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Dibuja etiqueta con el nombre
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Muestra la imagen con el resultado de la detección
    cv2.imshow('Video', frame)

    # Oprimir tecla q para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cierra la webcam
video_capture.release()
cv2.destroyAllWindows()
