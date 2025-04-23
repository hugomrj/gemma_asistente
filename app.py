
from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
import traceback
import markdown 
from bs4 import BeautifulSoup 

app = Flask(__name__)


# Configurar la API Key desde variable de entorno al inicio
API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyBlgLNetfWzsRwrSRNSE9TAoLkDDaHPEUk")




if not API_KEY:
    print("ADVERTENCIA: La variable de entorno GEMINI_API_KEY no está configurada.")
else:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error al configurar la API de Gemini: {e}")


def remove_markdown(text):
    """Convierte Markdown a HTML y luego extrae texto plano."""
    try:
        # Convertir Markdown a HTML
        html = markdown.markdown(text)
        # Extraer texto plano del HTML
        soup = BeautifulSoup(html, "html.parser")
        plain_text = soup.get_text()
        return plain_text
    except Exception as e:
        print(f"Error al intentar quitar Markdown: {e}")
        return text # Devolver texto original si falla la limpieza


def generate_response(pregunta):
    """
    Versión actualizada que usa genai.GenerativeModel y elimina el formato Markdown.
    """
    if not API_KEY:
         return "Error: La API Key de Gemini no fue configurada correctamente."

    if not pregunta or not isinstance(pregunta, str):
        return "La pregunta no es válida"

    try:
        model_name = "gemini-1.5-flash" # O el modelo que estés usando
        model = genai.GenerativeModel(model_name)

        generation_config = genai.types.GenerationConfig(
            temperature=0.9,
            top_p=1.0,
            top_k=40,
            max_output_tokens=2048
        )

        response = model.generate_content(
            pregunta,
            generation_config=generation_config
        )

        raw_text = "" # Inicializar texto crudo

        if not response.parts:
             block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else 'No especificada'
             safety_ratings = response.prompt_feedback.safety_ratings if response.prompt_feedback else 'No disponibles'
             print(f"Respuesta bloqueada. Razón: {block_reason}, Calificaciones: {safety_ratings}")
             return f"La respuesta fue bloqueada por motivos de seguridad o no se generó contenido. Razón: {block_reason}"

        if hasattr(response, 'text'):
             raw_text = response.text
        elif response.parts:
             raw_text = " ".join(part.text for part in response.parts if hasattr(part, 'text'))
        else:
             return "El modelo no generó una respuesta con texto."

        # --- Limpiar Markdown ---
        plain_response = remove_markdown(raw_text)
        # ------------------------

        return plain_response


    except Exception as e:
        print("--- Error Detallado en generate_response ---")
        traceback.print_exc()
        print("--- Fin Error Detallado ---")
        return f"Error al generar la respuesta con la API: {str(e)}"






@app.route('/')
def home():
    return render_template('index.html') # Asegúrate que exista este archivo







@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        if not request.is_json:
            return jsonify({'error': 'El contenido debe ser JSON (Content-Type: application/json)'}), 415

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos JSON en la solicitud'}), 400

        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'La clave "question" no puede estar vacía en el JSON'}), 400

        response_text = generate_response(question)

        if response_text.startswith("Error:") or "La respuesta fue bloqueada" in response_text:
             return jsonify({'error': response_text}), 500 # O el código apropiado

        return jsonify({'response': response_text})

    except Exception as e:
        print("--- Error Detallado en ask_question ---")
        traceback.print_exc()
        print("--- Fin Error Detallado ---")
        return jsonify({'error': f'Ocurrió un error inesperado en el servidor: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)