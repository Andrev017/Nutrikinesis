def detectar_sentadillas():
    import cv2
    import mediapipe as mp
    import numpy as np
    import os
    import pygame
    import math

    # Desactivar GPU (en caso de problemas con TensorFlow/MediaPipe)
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    # Inicializar pygame para la reproducción de música
    pygame.mixer.init()
    pygame.mixer.music.load('cancion.mp3')  # Reemplaza con la ruta de tu archivo de música

    # Inicializar MediaPipe y OpenCV
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    # Abrir la cámara predeterminada
    cap = cv2.VideoCapture(0)

    # Verificar si la cámara fue abierta correctamente
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        exit()
    else:
        print("Cámara abierta correctamente")
        pygame.mixer.music.play(-1)  # Reproducir la canción en bucle

    # Variables para contar sentadillas
    up = False
    down = False
    count = 0

    # Inicializar la detección de poses
    with mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar el frame.")
                break

            # Reducir el tamaño del frame para evitar sobrecarga de procesamiento
            frame = cv2.resize(frame, (640, 480))

            # Obtener dimensiones de la imagen
            height, width, _ = frame.shape

            # Convertir la imagen a RGB para MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Procesar la imagen para la detección de pose
            results = pose.process(frame_rgb)

            if results.pose_landmarks is not None:
                # Extraer coordenadas de cadera, rodilla y tobillo
                x1 = int(results.pose_landmarks.landmark[24].x * width)  # Cadera derecha
                y1 = int(results.pose_landmarks.landmark[24].y * height)

                x2 = int(results.pose_landmarks.landmark[26].x * width)  # Rodilla derecha
                y2 = int(results.pose_landmarks.landmark[26].y * height)

                x3 = int(results.pose_landmarks.landmark[28].x * width)  # Tobillo derecho
                y3 = int(results.pose_landmarks.landmark[28].y * height)

                # Calcular las distancias entre los puntos
                p1 = np.array([x1, y1])  # Cadera
                p2 = np.array([x2, y2])  # Rodilla
                p3 = np.array([x3, y3])  # Tobillo

                l1 = np.linalg.norm(p2 - p3)  # Distancia rodilla-tobillo
                l2 = np.linalg.norm(p1 - p3)  # Distancia cadera-tobillo
                l3 = np.linalg.norm(p1 - p2)  # Distancia cadera-rodilla

                # Calcular el ángulo de la rodilla
                try:
                    angle = math.degrees(math.acos((l1 ** 2 + l3 ** 2 - l2 ** 2) / (2 * l1 * l3)))
                except ValueError:
                    angle = 0

                # Contar las sentadillas basadas en el ángulo de la rodilla
                if angle >= 160:
                    up = True
                if up and not down and angle <= 70:
                    down = True
                if up and down and angle >= 160:
                    count += 1
                    up = False
                    down = False

                # Visualización del conteo de sentadillas
                aux_image = np.zeros(frame.shape, np.uint8)
                cv2.line(aux_image, (x1, y1), (x2, y2), (255, 255, 0), 20)
                cv2.line(aux_image, (x2, y2), (x3, y3), (255, 255, 0), 20)
                cv2.line(aux_image, (x1, y1), (x3, y3), (255, 255, 0), 5)
                contours = np.array([[x1, y1], [x2, y2], [x3, y3]])
                cv2.fillPoly(aux_image, pts=[contours], color=(128, 0, 250))

                # Mostrar el ángulo y el conteo en pantalla
                output = cv2.addWeighted(frame, 1, aux_image, 0.8, 0)
                cv2.circle(output, (x1, y1), 6, (0, 255, 255), 4)
                cv2.circle(output, (x2, y2), 6, (128, 0, 250), 4)
                cv2.circle(output, (x3, y3), 6, (255, 191, 0), 4)
                cv2.rectangle(output, (0, 0), (60, 60), (255, 255, 0), -1)
                cv2.putText(output, str(int(angle)), (x2 + 30, y2), 1, 1.5, (128, 0, 250), 2)
                cv2.putText(output, str(count), (10, 50), 1, 3.5, (128, 0, 250), 2)

                cv2.imshow("Output", output)

            # Mostrar el frame original
            cv2.imshow("Frame", frame)

            # Salir si se presiona la tecla ESC
            if cv2.waitKey(1) & 0xFF == 27:
                break

    # Detener la música y liberar la cámara
    pygame.mixer.music.stop()
    cap.release()
    cv2.destroyAllWindows()

    return "Detección de sentadillas en proceso..."
