from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
import traceback


from contexto import pregunta_con_contexto 

app = Flask(__name__)

# Clave de API para Gemini
API_KEY = "Agrega tu api key"


# Configura la API si se proporciona una clave válida
if not API_KEY:
    print("ADVERTENCIA: La variable de entorno GEMINI_API_KEY no está configurada.")
else:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error al configurar la API de Gemini: {e}")



# Función que genera la respuesta usando el modelo de Gemini
def generate_response(pregunta_con_contexto: str) -> str:
    if not API_KEY:
        return "Error: La API Key de Gemini no fue configurada correctamente."
    if not pregunta_con_contexto or not isinstance(pregunta_con_contexto, str):
        return "La pregunta no es válida"
    try:
        model_name = "gemma-3-27b-it"
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            temperature=0.9,
            top_p=1.0,
            top_k=40,
            max_output_tokens=2048
        )
        response = model.generate_content(
            pregunta_con_contexto,
            generation_config=generation_config
        )
        raw_text = ""
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
        
        return raw_text
    except Exception as e:
        print("--- Error Detallado en generate_response ---")
        traceback.print_exc()
        print("--- Fin Error Detallado ---")
        return f"Error al generar la respuesta con la API: {str(e)}"

# Ruta principal que sirve el HTML
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para recibir preguntas y retornar respuestas generadas
@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        if not request.is_json:
            return jsonify({'error': 'El contenido debe ser JSON (Content-Type: application/json)'}), 415
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos JSON en la solicitud'}), 400
        pregunta = data.get('question', '').strip()
        historial = data.get('history', [])
        if not pregunta:
            return jsonify({'error': 'La clave "question" no puede estar vacía en el JSON'}), 400
        contexto = pregunta_con_contexto(pregunta, historial)
        print("--- inicio contexto ---")
        print(contexto)
        print("--- fin contexto ---")
        response_text = generate_response(contexto)
        if response_text.startswith("Error:") or "La respuesta fue bloqueada" in response_text:
            return jsonify({'error': response_text}), 500
        return jsonify({'response': response_text})
    except Exception as e:
        print("--- Error Detallado en ask_question ---")
        traceback.print_exc()
        print("--- Fin Error Detallado ---")
        return jsonify({'error': f'Ocurrió un error inesperado en el servidor: {str(e)}'}), 500








# Inicia la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)





