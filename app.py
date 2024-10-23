from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import cv2
import base64
from io import BytesIO
import matplotlib.pyplot as plt

# Inicializa la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación

# Carga el modelo
model_path = 'modelo.keras'
model = load_model(model_path)

# Carga el DataFrame con los puntos faciales clave
keyfacial_df = pd.read_csv('data.csv')

# Convertir las cadenas de texto de las imágenes a matrices
# Asegúrate de que los datos en 'data.csv' estén en el formato correcto
keyfacial_df['Image'] = keyfacial_df['Image'].apply(lambda x: np.fromstring(x, dtype=int, sep=' ').reshape(96, 96))

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
    app.run(debug=True)
