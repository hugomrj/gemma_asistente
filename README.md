# Proyecto Flask y Gemma

Este es un proyecto básico que demuestra la integración de la potente API de Gemma con el framework web ligero Flask. Permite crear aplicaciones web interactivas que aprovechan las capacidades de generación de lenguaje, comprensión y más de Gemini.

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo:

1.  **Clona el repositorio:**

    ```bash
    git clone <URL del repositorio>
    cd <nombre del proyecto>
    ```

2.  **Crea un entorno virtual (recomendado):**

    Es una buena práctica aislar las dependencias de tu proyecto. Puedes crear un entorno virtual usando `venv` (si tienes Python 3.3+):

    ```bash
    python -m venv venv
    ```

    Y activarlo:

    * **En Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```
    * **En Windows:**
        ```bash
        venv\Scripts\activate
        ```

3.  **Instala las dependencias:**

    Asegúrate de tener instalado Flask y la librería de Gemini. Puedes instalar todas las dependencias listadas en el archivo `requirements.txt` (si lo tienes) con el siguiente comando:

    ```bash
    pip install -r requirements.txt
    ```bash
 

    O bien instalar las dependencias directamente

    ```bash
    pip install Flask
    pip install google-generativeai
    pip install Flask-CORS

    ```

    
    ejecutar en local    

    ```bash
    python app.py

    ```



4.  **Configura la API de Gemini:**

    Para usar la API de Gemini, necesitarás una clave de API. Puedes obtener una desde [Google Cloud AI Platform](https://console.cloud.google.com/vertex-ai).

    Una vez que tengas tu clave de API, puedes configurarla como una variable de entorno para mayor seguridad:

    ```bash
    export GOOGLE_API_KEY="TU_CLAVE_DE_API"
    ```




**Adicionales:**



```bash

sudo apt update
sudo apt install build-essential python3-dev libffi-dev

```
