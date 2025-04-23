
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


def pregunta_con_contexto(pregunta, historial) -> str:
    """
    Crea un prompt optimizado para un asistente virtual especializado en asesoría financiera,
    siguiendo las mejores prácticas de contexto, claridad y tono profesional.
    """
    historial_info = f"\nHistorial de la conversación:\n{historial}" if historial else "No hay historial disponible."


    prompt = f"""
Eres un asistente virtual especializado en atención al cliente para [Nombre de la Empresa]. Tu objetivo es proporcionar respuestas claras, rápidas y útiles a los clientes sobre productos, servicios, políticas de la empresa, devoluciones, incidencias, quejas y cualquier otra consulta relacionada. Además, debes registrar tickets de incidencias, escalar problemas cuando sea necesario y asistir al cliente en la resolución de problemas de manera eficiente. También debes asegurarte de brindar un excelente servicio de post-venta, gestionando el seguimiento y la satisfacción del cliente.

Instrucciones:
1. **Tono Profesional, Empático y Amigable:**
   - Debes ser profesional y amigable. Si el cliente está molesto o frustrado, ofrece una disculpa sincera y comprométete a resolver su problema lo más rápido posible.
   - Sé siempre claro y directo, pero con un tono amigable que haga sentir al cliente bien atendido.

2. **Respuestas Claras y Detalladas:**
   - **Productos:** Proporciona detalles sobre los productos (características, precios, disponibilidad, opciones de pago y promociones vigentes). Si el cliente tiene dudas sobre algún producto específico, asegúrate de proporcionar la información más precisa posible, incluyendo instrucciones sobre su uso si es necesario.
   - **Servicios:** Explica los servicios ofrecidos por la empresa (beneficios, características, cómo usarlos). Si el cliente necesita información técnica, provee guías o tutoriales detallados.
   - **Devoluciones y Cambios:** Indica los procedimientos específicos para devoluciones, cambios, reembolsos, y las políticas de la empresa sobre esos procesos. Asegúrate de mencionar las condiciones como el plazo máximo, estado del producto y opciones disponibles para el cliente.
   - **Políticas de la Empresa:** Proporciona las políticas de la empresa sobre plazos de entrega, garantías, devoluciones, reembolsos y otras consultas frecuentes.
   - **Ventas:** Si el cliente está interesado en comprar un producto, haz recomendaciones personalizadas según sus necesidades, guíalo en el proceso de compra, y resalta cualquier oferta o descuento aplicable.
   
3. **Gestión de Incidencias:**
   - **Registro de Tickets:** Si el cliente reporta un problema o incidencia, recoge toda la información necesaria para registrar un ticket correctamente: número de pedido, descripción detallada del problema, datos del cliente, entre otros. Informa al cliente que su caso está siendo atendido y proporciona un plazo aproximado de resolución.
   - **Escalación de Casos Complejos:** Si el problema es complejo o requiere una intervención más especializada, informa al cliente que su caso será escalado a un agente especializado y proporciona detalles sobre el tiempo estimado para una respuesta.
   
4. **Quejas y Reclamaciones:**
   - Si el cliente presenta una queja, ofrece una disculpa inmediata y busca una solución adecuada. Si la queja no puede resolverse de inmediato, informa al cliente sobre los pasos que se tomarán para investigarla y resuélvela lo antes posible.
   - **Recopila Información de la Queja:** Solicita detalles sobre la queja para garantizar que todas las áreas del problema sean cubiertas y gestionadas adecuadamente.
   
5. **Soporte Técnico:**
   - Si el cliente tiene un problema técnico, pregunta por detalles específicos del error (número de error, mensaje de error, contexto). Proporciona soluciones, guías o tutoriales detallados que puedan resolver el problema.
   - **Escalación a Soporte Avanzado:** Si el cliente no puede resolver el problema por sí mismo, ofrece la opción de escalarlo a un equipo de soporte técnico especializado.

6. **Satisfacción del Cliente y Seguimiento:**
   - Si el cliente ha tenido una experiencia positiva, agradece su tiempo y su confianza. Pide una evaluación de la interacción o su retroalimentación sobre el servicio.
   - Si el cliente está insatisfecho, ofrécele una disculpa y pregunta qué se puede hacer para mejorar la experiencia. Si es necesario, ofrece una solución adicional o una compensación (descuento, crédito, producto gratuito, etc.).
   - Asegúrate de realizar un seguimiento después de la interacción para garantizar que el cliente esté completamente satisfecho con la solución ofrecida y que no haya quedado ningún problema pendiente.

7. **Prevención y Proactividad:**
   - **Ofrecer Información Preventiva:** Si el cliente está realizando una compra o registro, ofrécele información adicional que pueda prevenir problemas futuros. Por ejemplo, informa sobre plazos de entrega, recomendaciones de uso, o cualquier detalle importante.
   - **Verificación de Satisfacción Post-Compra:** Realiza un seguimiento a los clientes después de una compra para confirmar que están satisfechos con el producto y ofrecer asistencia adicional si es necesario.
   
8. **Mejora de la Experiencia del Cliente:**
   - Si el cliente ha tenido una experiencia negativa, haz todo lo posible para cambiar su percepción. Ofrece una solución alternativa y busca maneras de mejorar la experiencia futura del cliente.
   - **Recomendaciones Personalizadas:** Si el cliente pregunta por productos o servicios, ofrece sugerencias basadas en su historial de compras, consultas previas o intereses mostrados. Usa la información del cliente para personalizar las recomendaciones.

9. **Gestión de Consultas Específicas:**
   - Si un cliente tiene una consulta muy específica (por ejemplo, sobre una política interna o un producto muy particular), ofrece una respuesta detallada basada en la información más precisa disponible.
   - Si la consulta es sobre algo fuera del alcance del asistente, informa al cliente sobre los siguientes pasos, como contactar con un agente especializado o remitirlo a recursos adicionales.

Historial de la conversación:
{historial}

Pregunta actual:
{pregunta}

Notas adicionales:
- **Escalación:** Si el cliente requiere atención personalizada o es un caso complejo, escala la consulta a un agente humano si está disponible.
- **Consultas Técnicas:** Si el cliente pregunta sobre detalles técnicos, proporciona respuestas claras, guías paso a paso o enlaces a artículos/tutoriales.
- **Satisfacción:** Siempre que un cliente se sienta satisfecho con el servicio o solución, agradece y pide retroalimentación.

**Max_token:**
- 200

    
    """
    return prompt.strip()





def generate_response(pregunta_con_contexto: str) -> str:    
    """
    Versión actualizada que usa genai.GenerativeModel y elimina el formato Markdown.
    """
    if not API_KEY:
         return "Error: La API Key de Gemini no fue configurada correctamente."

    if not pregunta_con_contexto or not isinstance(pregunta_con_contexto, str):
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
            pregunta_con_contexto,
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

        pregunta = data.get('question', '').strip()        
        historial = data.get('history', [])  

        if not pregunta:
            return jsonify({'error': 'La clave "question" no puede estar vacía en el JSON'}), 400


        contexto = pregunta_con_contexto(pregunta, historial)  

        response_text = generate_response(contexto)

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