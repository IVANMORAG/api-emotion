from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import cv2
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import os

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configura CORS para permitir la URL de tu aplicación en Render
CORS(app, resources={r"/predict": {"origins": "*"}})

# Configura el puerto
port = int(os.environ.get("PORT", 5000))  # Usa el puerto proporcionado por Render

# Ruta de bienvenida
@app.route('/')
def home():
    return render_template('index.html')

# Carga el modelo
model_path = 'modelo.keras'
model = load_model(model_path)

# Carga el DataFrame con los puntos faciales clave
keyfacial_df = pd.read_csv('data.csv')

def decode_image(image_string):
    try:
        image_string = image_string.strip()  # Elimina espacios en blanco
        image_data = np.frombuffer(base64.b64decode(image_string), dtype=np.uint8)
        if image_data.size == 9216:  # 96*96
            return image_data.reshape(96, 96)
        else:
            print(f"Error: tamaño de la imagen inesperado: {image_data.size}")
            return None
    except Exception as e:
        print(f"Error al decodificar la imagen: {e}")
        return None

# Convertir las cadenas de texto de las imágenes a matrices
keyfacial_df['Image'] = keyfacial_df['Image'].apply(decode_image)

@app.route('/predict', methods=['POST'])
def predict():
    # Verifica que se haya enviado una imagen
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    # Lee la imagen enviada
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    # Guarda las dimensiones originales de la imagen
    original_height, original_width = img.shape
    print(f'Dimensiones de la imagen original: {original_height}x{original_width}')

    # Preprocesa la imagen
    img_resized = cv2.resize(img, (96, 96))  # Redimensiona a 96x96
    img_resized = img_resized.reshape(1, 96, 96, 1).astype('float32') / 255  # Normaliza

    # Realiza la predicción
    prediction = model.predict(img_resized)
    predicted_class = np.argmax(prediction)

    # Define las clases
    classes = ['Clase A', 'Clase B', 'Clase C']  # Ajusta esto con tus clases reales
    print(f'Clase predicha: {predicted_class}, Confianza: {prediction[0][predicted_class]}')

    # Obtén los puntos clave de la clase predicha
    result = {
        'predicted_class': classes[predicted_class],
        'confidence': float(prediction[0][predicted_class])
    }

    if predicted_class < len(keyfacial_df):
        keypoints = keyfacial_df.iloc[predicted_class][:-1].values.reshape(-1, 2)
        print(f'Puntos clave para la clase {predicted_class}: {keypoints}')

        # Escala los puntos clave a las dimensiones originales de la imagen
        scaled_keypoints = keypoints * (original_width / 96, original_height / 96)

        # Visualiza la imagen con los puntos clave
        plt.imshow(img, cmap='gray')  # Usa la imagen original
        for (x, y) in scaled_keypoints:
            plt.plot(x, y, 'rx')  # Dibuja los puntos clave

        # Guarda la imagen con los puntos clave en un buffer
        buf = BytesIO()
        plt.axis('off')
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)

        # Convierte la imagen a base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        result['image'] = f"data:image/png;base64,{img_base64}"
    else:
        result['image'] = None

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)  # Asegúrate de que el puerto sea el correcto
