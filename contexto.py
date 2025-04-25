import datetime
import os
import re # Necesario para búsqueda por características más flexible

# -------------------------------------------------------------------
# DEFINICIÓN DEL PROMPT Y PALABRAS CLAVE
# -------------------------------------------------------------------

def pregunta_con_contexto(pregunta, historial) -> str:
    """
    Crea un prompt optimizado para un asistente virtual especializado en ventas,
    siguiendo las mejores prácticas de contexto, claridad y tono persuasivo y amable.
    """
    historial = f"\nHistorial de la conversación:\n{historial}" if historial else "No hay historial disponible."
    condiciones_dinamicas = generar_condiciones_dinamicas(pregunta)
    if condiciones_dinamicas.strip():
        condiciones_dinamicas = "\n🧠 **Información relevante encontrada para tu consulta:**\n" + condiciones_dinamicas # Mensaje más claro
    prompt = f"""
## Rol del Asistente:
Eres un asistente virtual especializado en **ventas** para Comercial Nova. Tu misión es ayudar a los clientes a elegir productos o servicios adecuados, brindar información clara y útil sobre precios, promociones, formas de pago, disponibilidad y beneficios, además de guiarlos paso a paso durante el proceso de compra. También brindás atención post-venta para asegurar la satisfacción del cliente.

Instrucciones:
1. **Tono Profesional, Cercano y Persuasivo:**
   - "Si el usuario inicia con un saludo (ej: 'hola'), responde con un saludo amable. En otros casos, ve directo al tema."
   - Solo saludá si la **pregunta actual** no contiene palabras de saludo.
   - Ayuda al cliente a sentirse seguro con su compra.
   - Si el cliente tiene dudas, explícalas con paciencia y seguridad, buscando cerrar la venta sin ser insistente.

2. **Información sobre Productos y Servicios:**
   - Brinda detalles sobre productos: características, beneficios, precios, disponibilidad, formas de pago, promociones y garantías.
   - Ofrecé recomendaciones personalizadas según lo que el cliente necesita o está buscando. Basado en el historial y la pregunta actual.

3. **Proceso de Compra:**
   - Guiá al cliente en los pasos para comprar: cómo hacerlo, qué opciones tiene y cómo confirmar su compra.
   - Si el cliente tiene dificultades, resolvélas de forma simple y directa.

4. **Promociones y Descuentos:**
   - Informá sobre cualquier promoción activa, cupones, combos o descuentos relevantes a la consulta.
   - Aprovechá las oportunidades para sugerir productos complementarios o de mayor valor (upselling/cross-selling) si es pertinente.

5. **Atención Post-Venta:**
   - Informá sobre tiempos de entrega, seguimiento de pedidos, cambios o devoluciones si lo solicita.
   - Consultá si quedó conforme con su compra y ofrecé asistencia adicional si es necesario.

6. **Escalación si es Necesario:**
   - Si el cliente tiene una consulta muy específica que no puedes resolver (ej: stock en tiempo real en una sucursal específica, problema técnico complejo) o requiere atención humana, informá que vas a escalar su caso y derivarlo al equipo adecuado.

7. **Detecta emociones o indecisión:**
   - Si notas que el cliente está dudando o frustrado (palabras como "no sé", "caro", "duda", "complicado"), tranquilízalo, valida su sentir y ofrécele alternativas, beneficios adicionales o explica mejor el valor del producto.

8. **Al finalizar, pide feedback:**
   - Pregunta amablemente si la atención fue útil y si hay algo más en lo que puedas ayudar.

{condiciones_dinamicas}
{historial}

Pregunta actual:
{pregunta}

Notas adicionales:
- Si la consulta es sobre un tipo de producto (ej: "celulares", "notebooks"), muestra los productos disponibles de esa categoría con sus detalles clave (precio, características principales).
- Si el cliente está listo para comprar, guiá el proceso de cierre de venta.
- Si el cliente no sabe qué quiere, ayudalo a decidir con preguntas breves ("¿Qué uso le darías?", "¿Qué presupuesto tienes?") o sugerencias basadas en productos populares.
- Siempre agradecé su interés y ofrecé ayuda adicional antes de terminar.
- Si el cliente ya compró (basado en historial), consultá si quedó conforme y ofrecé productos relacionados o soporte.
**Max_token:**
- 200
    """

    guardar_prompt_log(prompt.strip())

    return prompt.strip()







# Bloques de palabras clave (podrían estar en un archivo aparte como constants.py)
PALABRAS_CLAVE = {
    "promocion": {"promoción", "oferta", "ofertas", "descuento", "cupón", "rebaja", "promo"},
    "politicas": {"garantía", "devolución", "reembolso", "cambio", "entrega", "envío", "política", "instalación"},
    "precio": {"precio", "precios", "cuánto cuesta", "valor", "costó", "cuanto sale", "cotización"},
    "caracteristicas": {
        # Generales
        "cámara", "batería", "almacenamiento", "color", "pantalla", "ram", "procesador", "tamaño", "memoria",
        # Específicas TV/Monitor
        "resolución", "pulgadas", "hz", "hercios", "oled", "qled", "hdmi",
        # Específicas Audio
        "bluetooth", "cancelación", "ruido", "inalámbrico", "potencia", "watts",
        # Específicas Smartwatch
        "gps", "resistencia", "agua", "cardiaco", "ecg", "oxígeno",
        # Específicas Consola
        "juegos", "fps", "disco", "ssd", "gráficos", "teraflops"
    },
    "categorias": {
        "celular", "celulares", "teléfono", "móvil",
        "notebook", "notebooks", "laptop", "portátil",
        "tablet", "tablets", "tableta",
        "accesorio", "accesorios", "auriculares", "cargador", "funda", "teclado", "mouse",
        "smartwatch", "reloj", "relojes",
        "consola", "consolas", "videojuego", "videojuegos", "playstation", "xbox", "nintendo",
        "tv", "televisor", "televisores", "tele", "pantalla",
        "audio", "sonido", "parlante", "altavoz", "auricular", "barra"
     }
}

def generar_condiciones_dinamicas(pregunta: str) -> str:
    """Genera texto con información relevante basado en las palabras clave detectadas en la pregunta."""
    condiciones = []
    pregunta_lower = pregunta.lower()

    # 1. Detección más eficiente usando conjuntos
    palabras_en_pregunta = set(re.findall(r'\b\w+\b', pregunta_lower)) # Extrae palabras individuales

    # 2. Manejo de promociones optimizado
    if PALABRAS_CLAVE["promocion"] & palabras_en_pregunta:
        promos = obtener_promociones_actuales()
        # Filtrar promos activas (opcional, si la fecha es relevante)
        # from datetime import datetime
        # hoy = datetime.now().strftime("%d/%m/%Y")
        # promos_activas = [p for p in promos if p['valido_hasta'] >= hoy] # Simplificado, cuidado con formato fecha
        promos_texto = "\n".join([
            f"• 🎁 **{p['nombre']}**: {p['detalle']} (Válido hasta: {p['valido_hasta']})"
            for p in promos # Usar promos_activas si se filtra
        ])
        if promos_texto:
             condiciones.append(f"📢 **Promociones vigentes:**\n{promos_texto}")
        else:
             condiciones.append("📢 No tenemos promociones especiales activas en este momento, pero nuestros precios son muy competitivos.")

    # 3. Manejo de políticas con detección mejorada
    palabras_politica_encontradas = PALABRAS_CLAVE["politicas"] & palabras_en_pregunta
    if palabras_politica_encontradas:
        politicas = obtener_politicas_completas()
        politicas_texto = "\n".join([
            # Muestra solo las políticas mencionadas o todas si es genérico ("política")
            f"• 🔧 **{key.capitalize()}**: {value}"
            for key, value in politicas.items() if key in palabras_politica_encontradas or "política" in palabras_politica_encontradas
        ])
        condiciones.append(f"📜 **Información sobre políticas ({', '.join(p.capitalize() for p in palabras_politica_encontradas)}):**\n{politicas_texto}")

    # 4. Búsqueda por categoría optimizada (ESTA ES LA CLAVE PARA TU REQUERIMIENTO)
    #   Usamos intersección para ver qué categorías de nuestra lista están en la pregunta
    categorias_solicitadas = PALABRAS_CLAVE["categorias"] & palabras_en_pregunta
    catalogo = None # Cargar solo si es necesario

    if categorias_solicitadas:
        if catalogo is None: catalogo = obtener_catalogo_completo()
        for categoria_keyword in categorias_solicitadas:
            # Mapear palabra clave a nombre de categoría real en el catálogo (ej: "celulares" -> "celular")
            categoria_real = next((cat for cat, data in catalogo.items() if categoria_keyword in PALABRAS_CLAVE["categorias"] and categoria_keyword in cat or cat in categoria_keyword), None)
            # Intento adicional por si la palabra clave es parte del nombre de la categoría (ej: "playstation" -> "consola")
            if not categoria_real:
                 categoria_real = next((cat for cat, data in catalogo.items() if categoria_keyword in cat), None)

            if categoria_real and categoria_real in catalogo:
                productos_texto = generar_info_productos(catalogo[categoria_real])
                if productos_texto:
                    condiciones.append(f" Búsqueda por Categoría: **{categoria_real.capitalize()}** \n{productos_texto}")
                else:
                     condiciones.append(f" No encontré productos específicos en la categoría '{categoria_real.capitalize()}' en este momento.")
            #else:
            #    print(f"Debug: No se encontró mapeo para keyword '{categoria_keyword}'") # Para depuración

    # 5. Búsqueda por precio más precisa
    if PALABRAS_CLAVE["precio"] & palabras_en_pregunta:
        if catalogo is None: catalogo = obtener_catalogo_completo()
        if categorias_solicitadas: # Si ya se pidió categoría, mostrar precios de esa
             for categoria_real in {cat for cat_key in categorias_solicitadas
                                   for cat, data in catalogo.items()
                                   if cat_key in PALABRAS_CLAVE["categorias"] and (cat_key in cat or cat in cat_key)}:
                if categoria_real in catalogo:
                    precios_texto = "\n".join([
                        f"• {prod['nombre']}: {prod['precio_usd']:.2f} USD / {prod['precio_gs']:,.0f} Gs".replace(",",".") # Formato mejorado
                        for prod in catalogo[categoria_real]
                    ])
                    condiciones.append(f" **Precios en {categoria_real.capitalize()}:**\n{precios_texto}")
        else: # Si solo se pide precio sin categoría, mostrar algunos ejemplos o pedir aclaración
             condiciones.append(" Sobre qué categoría o producto te gustaría saber el precio? Tenemos celulares, notebooks, TVs y más.")


    # 6. Búsqueda por características optimizada
    caracteristicas_solicitadas = PALABRAS_CLAVE["caracteristicas"] & palabras_en_pregunta
    if caracteristicas_solicitadas:
        if catalogo is None: catalogo = obtener_catalogo_completo()
        # Pasar las características detectadas a la función de búsqueda
        resultados = buscar_por_caracteristicas(pregunta_lower, caracteristicas_solicitadas, catalogo)
        if resultados:
            condiciones.append(f" **Productos relacionados con '{', '.join(caracteristicas_solicitadas)}':**\n{resultados}")
        else:
            condiciones.append(f" No encontré productos que coincidan específicamente con las características '{', '.join(caracteristicas_solicitadas)}'. ¿Podrías darme más detalles?")


    # 7. Búsqueda de productos específicos (por nombre)
    #    Lista de nombres de productos comunes para búsqueda rápida
    nombres_productos_comunes = {"iphone", "galaxy", "macbook", "ipad", "airpods", "ps5", "playstation 5", "xbox series", "apple watch", "galaxy watch"}
    palabras_producto_detectadas = {palabra for palabra in nombres_productos_comunes if palabra in pregunta_lower}

    if palabras_producto_detectadas:
         if catalogo is None: catalogo = obtener_catalogo_completo()
         productos_encontrados_texto = []
         for categoria, productos in catalogo.items():
             for prod in productos:
                 nombre_prod_lower = prod['nombre'].lower()
                 # Comprobar si alguna palabra detectada está en el nombre del producto
                 if any(palabra_detectada in nombre_prod_lower for palabra_detectada in palabras_producto_detectadas):
                     precio_gs_f = f"{prod['precio_gs']:,.0f}".replace(",", ".")
                     producto_detalle = (
                         f"📌 **{prod['nombre']}** ({categoria.capitalize()})\n"
                         f"   💵 Precio: ${prod['precio_usd']:.2f}$ USD / ${precio_gs_f}$ Gs\n"
                         f"   🎨 Colores disponibles: {', '.join(prod['colores'])}\n"
                         f"   💾 Almacenamiento: {', '.join(prod.get('almacenamiento', ['N/D']))}\n"
                         f"   ⚙️ Destacado: {'; '.join(prod['caracteristicas'][:3])}..." # Primeras 3 características
                     )
                     productos_encontrados_texto.append(producto_detalle)

         if productos_encontrados_texto:
             condiciones.append(f" **Información sobre productos específicos mencionados:**\n" + "\n\n".join(productos_encontrados_texto))


    # 8. Caso genérico "productos" (si no se activó nada más específico)
    #    Se activa si se dice "productos" pero no una categoría o nombre específico.
    if not categorias_solicitadas and not palabras_producto_detectadas and not caracteristicas_solicitadas and any(p in pregunta_lower for p in ["producto", "productos", "artículo", "artículos", "item", "items"]):
         if catalogo is None: catalogo = obtener_catalogo_completo()
         condiciones.append(" Tenemos una gran variedad de productos electrónicos. ¿Te interesa alguna categoría en particular como celulares, notebooks, TVs, consolas, audio o accesorios?")


    return "\n\n".join(condiciones) if condiciones else ""


# -------------------------------------------------------------------
# MÓDULO DE DATOS (Considera mover a un archivo JSON si crece mucho)
# -------------------------------------------------------------------
def obtener_politicas_completas():
    """Devuelve un diccionario con las políticas de la tienda."""
    return {
        "garantia": "12 meses contra defectos de fábrica en la mayoría de los productos. Notebooks y TVs pueden tener garantía extendida del fabricante (consultar modelo).",
        "devolucion": "10 días corridos desde la compra para devoluciones si el producto está sin uso, en su empaque original sellado y con factura.",
        "cambio": "30 días para cambios por otro producto (aplican condiciones de devolución). Si hay diferencia de precio, se ajusta.",
        "reembolso": "Se procesa dentro de los 7 días hábiles posteriores a la aceptación de la devolución, por el mismo medio de pago original.",
        "entrega": "Envío estándar 24-72hs hábiles en Asunción y Gran Asunción (costo según zona, gratis para compras > 1.500.000 Gs). Envíos al interior vía transportadora (costo a cargo del cliente).",
        "instalación": "Ofrecemos servicio de instalación básica para TVs y configuración inicial para notebooks con costo adicional (consultar precios)."
    }

def obtener_promociones_actuales():
    """Devuelve una lista de diccionarios con promociones vigentes."""
    # Asegúrate de mantener estas fechas actualizadas o implementar lógica para filtrar
    return [
        {
            "nombre": "TecnoFest Verano",
            "detalle": "Hasta 25% de descuento en Smartphones seleccionados y 12 cuotas sin interés con bancos asociados.",
            "valido_hasta": "31/05/2025" # Ejemplo: Usar formato AAAA-MM-DD para facilitar comparación
        },
        {
            "nombre": "Vuelta al Cole Tech",
            "detalle": "Notebooks y Tablets con 10% OFF + Mochila de regalo en modelos seleccionados.",
            "valido_hasta": "15/03/2025" # Ejemplo pasado
        },
        {
            "nombre": "Combo Gamer Pro",
            "detalle": "Lleva una Consola PS5 + Juego de lanzamiento + Auriculares Gamer con 1.000.000 Gs de ahorro.",
            "valido_hasta": "30/04/2025"
        },
         {
            "nombre": "Audio Inmersivo",
            "detalle": "20% de descuento en Barras de Sonido y Auriculares con cancelación de ruido.",
            "valido_hasta": "15/05/2025"
        }
    ]

def obtener_catalogo_completo():
    """Devuelve el catálogo completo de productos por categoría."""
    USD_TO_GS = 7450  # Actualizar tipo de cambio periódicamente

    return {
        "celular": [
            {
                "nombre": "iPhone 16 Pro", # Modelo hipotético futuro
                "precio_usd": 1199, "precio_gs": 1199 * USD_TO_GS,
                "colores": ["Titanio Natural", "Titanio Azul", "Titanio Blanco", "Titanio Negro"],
                "almacenamiento": ["128GB", "256GB", "512GB", "1TB"],
                "caracteristicas": ["Chip A18 Pro", "Pantalla Super Retina XDR ProMotion", "Sistema de cámaras Pro avanzado 48MP", "Botón de Acción configurable", "USB-C Thunderbolt"]
            },
            {
                "nombre": "iPhone 16", # Modelo hipotético futuro
                "precio_usd": 899, "precio_gs": 899 * USD_TO_GS,
                "colores": ["Azul", "Rosa", "Verde", "Negro", "Blanco"],
                "almacenamiento": ["128GB", "256GB", "512GB"],
                "caracteristicas": ["Chip A17 (mejorado)", "Pantalla Super Retina XDR", "Cámara dual 48MP", "Dynamic Island", "USB-C"]
            },
            {
                "nombre": "Samsung Galaxy S25 Ultra", # Modelo hipotético futuro
                "precio_usd": 1299, "precio_gs": 1299 * USD_TO_GS,
                "colores": ["Phantom Black", "Phantom Silver", "Emerald Green", "Sapphire Blue"],
                "almacenamiento": ["256GB", "512GB", "1TB"],
                "caracteristicas": ["Pantalla Dynamic AMOLED 3X 120Hz", "Procesador Snapdragon Gen 4 for Galaxy", "Cámara principal 200MP con IA", "S-Pen integrado", "Batería 5500mAh"]
            },
             {
                "nombre": "Samsung Galaxy A56", # Modelo hipotético futuro
                "precio_usd": 450, "precio_gs": 450 * USD_TO_GS,
                "colores": ["Awesome Black", "Awesome White", "Awesome Blue"],
                "almacenamiento": ["128GB", "256GB"],
                "caracteristicas": ["Pantalla Super AMOLED 120Hz", "Cámara 64MP OIS", "Batería 5000mAh", "Resistencia IP67", "Procesador Exynos eficiente"]
            },
            {
                "nombre": "Xiaomi 15 Pro", # Modelo hipotético futuro
                "precio_usd": 950, "precio_gs": 950 * USD_TO_GS,
                "colores": ["Negro Cerámico", "Blanco Nieve", "Verde Bosque"],
                "almacenamiento": ["256GB", "512GB"],
                "caracteristicas": ["Sensor de cámara 1 pulgada", "Lentes Leica Summilux", "Pantalla LTPO AMOLED 144Hz", "Carga rápida 120W", "Snapdragon Gen 4"]
            }
        ],
        "notebook": [
            {
                "nombre": "MacBook Air 13\" M3",
                "precio_usd": 1099, "precio_gs": 1099 * USD_TO_GS,
                "colores": ["Medianoche", "Blanco estelar", "Gris espacial", "Plata"],
                "almacenamiento": ["256GB SSD", "512GB SSD"], "ram": ["8GB", "16GB"],
                "caracteristicas": ["Chip M3 Apple Silicon", "Pantalla Liquid Retina 13.6\"", "Hasta 18h de batería", "Diseño ultra delgado y ligero", "Magic Keyboard"]
            },
            {
                "nombre": "MacBook Pro 14\" M3 Pro",
                "precio_usd": 1999, "precio_gs": 1999 * USD_TO_GS,
                "colores": ["Negro espacial", "Plata"],
                "almacenamiento": ["512GB SSD", "1TB SSD"], "ram": ["18GB", "36GB"],
                "caracteristicas": ["Chip M3 Pro Apple Silicon", "Pantalla Liquid Retina XDR 14.2\"", "Rendimiento extremo para profesionales", "Sistema de sonido avanzado", "Puertos Pro (HDMI, SDXC)"]
            },
            {
                "nombre": "Dell XPS 15 (Modelo 9540)", # Modelo hipotético
                "precio_usd": 1650, "precio_gs": 1650 * USD_TO_GS,
                "colores": ["Platino", "Grafito"],
                "almacenamiento": ["512GB SSD", "1TB SSD", "2TB SSD"], "ram": ["16GB", "32GB", "64GB"],
                "caracteristicas": ["Procesador Intel Core Ultra 7/9", "Pantalla InfinityEdge OLED 3.5K táctil (opcional)", "Gráficos NVIDIA GeForce RTX 4050/4060 (opcional)", "Chasis de aluminio premium", "Windows 11 Pro"]
            },
             {
                "nombre": "HP Spectre x360 14 (2025)", # Modelo hipotético
                "precio_usd": 1400, "precio_gs": 1400 * USD_TO_GS,
                "colores": ["Nightfall Black", "Poseidon Blue"],
                "almacenamiento": ["512GB SSD", "1TB SSD"], "ram": ["16GB", "32GB"],
                "caracteristicas": ["Diseño convertible 2-en-1", "Pantalla OLED 2.8K 120Hz", "Procesador Intel Core Ultra 7", "Lápiz óptico incluido", "Cámara IA 5MP IR"]
            }
        ],
        "tablet": [
            {
                "nombre": "iPad Pro 11\" M3", # Modelo hipotético
                "precio_usd": 999, "precio_gs": 999 * USD_TO_GS,
                "colores": ["Plata", "Gris espacial"],
                "almacenamiento": ["128GB", "256GB", "512GB", "1TB", "2TB"],
                "caracteristicas": ["Chip M3 Apple Silicon", "Pantalla Ultra Retina XDR (OLED)", "Diseño más delgado", "Apple Pencil Pro compatible", "Face ID"]
            },
             {
                "nombre": "iPad Air 13\" M2",
                "precio_usd": 799, "precio_gs": 799 * USD_TO_GS,
                "colores": ["Azul", "Púrpura", "Blanco estelar", "Gris espacial"],
                "almacenamiento": ["128GB", "256GB", "512GB", "1TB"],
                "caracteristicas": ["Chip M2 Apple Silicon", "Pantalla Liquid Retina 13\"", "Apple Pencil Pro compatible", "Touch ID en botón superior", "Cámara frontal horizontal"]
            },
            {
                "nombre": "Samsung Galaxy Tab S10 Ultra", # Modelo hipotético
                "precio_usd": 1100, "precio_gs": 1100 * USD_TO_GS,
                "colores": ["Beige", "Grafito"],
                "almacenamiento": ["256GB", "512GB", "1TB"], "ram": ["12GB", "16GB"],
                "caracteristicas": ["Pantalla Dynamic AMOLED 2X 14.6\"", "Procesador Snapdragon Gen 4 for Galaxy", "S-Pen incluido (baja latencia)", "Resistencia IP68", "Samsung DeX mejorado"]
            }
        ],
         "smartwatch": [
            {
                "nombre": "Apple Watch Series 10", # Modelo hipotético
                "precio_usd": 399, "precio_gs": 399 * USD_TO_GS,
                "colores": ["Aluminio: Medianoche, Blanco Estelar, Plata, Rojo (Product)RED", "Acero: Grafito, Oro, Plata"],
                "tamaño": ["41mm", "45mm"],
                "caracteristicas": ["Nuevo diseño (posiblemente más delgado)", "Sensor de presión arterial (rumoreado)", "Detección de apnea del sueño (rumoreado)", "Chip S10 más rápido", "watchOS 11"]
            },
             {
                "nombre": "Apple Watch Ultra 3", # Modelo hipotético
                "precio_usd": 799, "precio_gs": 799 * USD_TO_GS,
                "colores": ["Titanio natural (nuevos acabados posibles)"],
                "tamaño": ["49mm"],
                "caracteristicas": ["Chip S10", "Pantalla MicroLED (rumoreado, podría retrasarse)", "Mayor duración de batería", "Funciones avanzadas para deportes extremos", "Resistencia grado militar"]
             },
             {
                "nombre": "Samsung Galaxy Watch 7 Pro", # Modelo hipotético
                "precio_usd": 449, "precio_gs": 449 * USD_TO_GS,
                "colores": ["Negro Titanio", "Gris Titanio"],
                "tamaño": ["47mm"],
                "caracteristicas": ["Wear OS Powered by Samsung", "Nuevo procesador Exynos W1000 (rumoreado)", "Sensor BioActive (ECG, Presión Arterial, Composición Corporal)", "Batería de larga duración (hasta 80h)", "Bisel giratorio (posiblemente solo en Classic)"]
             }
        ],
        "consola": [
            {
                "nombre": "PlayStation 5 Slim (PS5 Slim)",
                "precio_usd": 499, "precio_gs": 499 * USD_TO_GS,
                "colores": ["Blanco/Negro"],
                "almacenamiento": ["1TB SSD (útil ~825GB)"],
                "caracteristicas": ["Diseño más compacto", "Lector de discos Blu-ray Ultra HD (extraíble en versión digital)", "CPU AMD Zen 2 8-core", "GPU AMD RDNA 2 (10.3 TFLOPS)", "Audio 3D TempestTech", "Retrocompatible con PS4"]
            },
            {
                "nombre": "Xbox Series X",
                "precio_usd": 499, "precio_gs": 499 * USD_TO_GS,
                "colores": ["Negro"],
                "almacenamiento": ["1TB NVMe SSD (útil ~802GB)"],
                "caracteristicas": ["La consola más potente (12 TFLOPS)", "CPU AMD Zen 2 8-core", "GPU AMD RDNA 2", "Quick Resume", "Xbox Game Pass (requiere suscripción)", "Retrocompatible con Xbox One, 360, Original"]
             },
            {
                "nombre": "Nintendo Switch - Modelo OLED",
                "precio_usd": 349, "precio_gs": 349 * USD_TO_GS,
                "colores": ["Blanco", "Rojo Neón/Azul Neón"],
                "almacenamiento": ["64GB internos (ampliable con microSD)"],
                "caracteristicas": ["Pantalla OLED vibrante de 7 pulgadas", "Modos de juego: TV, sobremesa, portátil", "Joy-Con extraíbles", "Amplio catálogo de juegos exclusivos", "Soporte ajustable ancho"]
             }
        ],
         "tv": [
             {
                "nombre": "Samsung 65\" QN90D Neo QLED 4K TV", # Modelo hipotético 2025
                "precio_usd": 2200, "precio_gs": 2200 * USD_TO_GS,
                "colores": ["Negro"], "tamaño": ["65 pulgadas"],
                "caracteristicas": ["Tecnología Quantum Mini LED", "Resolución 4K UHD (3840x2160)", "Procesador NQ4 AI Gen2", "Tasa de refresco 120Hz (hasta 144Hz para gaming)", "Smart TV Tizen OS", "Sonido OTS+ (Object Tracking Sound+)"]
             },
             {
                "nombre": "LG 55\" C4 OLED evo 4K TV", # Modelo 2024 real
                "precio_usd": 1800, "precio_gs": 1800 * USD_TO_GS,
                "colores": ["Negro"], "tamaño": ["55 pulgadas"],
                "caracteristicas": ["Panel OLED evo autoiluminado", "Resolución 4K UHD", "Procesador α9 AI Gen7", "Perfect Black, Contraste Infinito", "Dolby Vision, Dolby Atmos", "webOS 24 Smart TV", "Ideal para cine y gaming (G-Sync, FreeSync)"]
             },
              {
                "nombre": "Sony 75\" BRAVIA 7 (XR70) QLED 4K TV", # Modelo 2024 real
                "precio_usd": 2800, "precio_gs": 2800 * USD_TO_GS,
                "colores": ["Negro"], "tamaño": ["75 pulgadas"],
                "caracteristicas": ["Panel QLED (Mini LED Backlight)", "Resolución 4K UHD", "Procesador XR", "XR Backlight Master Drive", "Google TV", "Acoustic Multi-Audio+", "Perfect for PlayStation 5"]
              }
         ],
         "audio": [
             {
                "nombre": "Sony WH-1000XM6 Auriculares inalámbricos", # Modelo hipotético
                "precio_usd": 399, "precio_gs": 399 * USD_TO_GS,
                "colores": ["Negro", "Plata", "Azul Noche"],
                "caracteristicas": ["Cancelación de ruido líder en la industria (mejorada)", "Nuevo diseño más cómodo", "Procesador de audio V2 (hipotético)", "Hasta 35 horas de batería (con NC)", "Conexión multipunto", "Audio Hi-Res inalámbrico (LDAC)"]
             },
             {
                "nombre": "Bose QuietComfort Ultra Headphones", # Modelo real
                "precio_usd": 429, "precio_gs": 429 * USD_TO_GS,
                "colores": ["Black", "White Smoke"],
                "caracteristicas": ["Cancelación de ruido de clase mundial", "Bose Immersive Audio (audio espacial)", "Modo Aware (transparencia)", "Ajuste cómodo y estable", "Hasta 24 horas de batería"]
             },
             {
                "nombre": "JBL Charge 6 Altavoz Bluetooth portátil", # Modelo hipotético
                "precio_usd": 199, "precio_gs": 199 * USD_TO_GS,
                "colores": ["Negro", "Azul", "Rojo", "Verde Camuflado"],
                "caracteristicas": ["Sonido JBL Original Pro potente", "Hasta 25 horas de reproducción", "Resistente al agua y al polvo (IP67)", "Powerbank incorporado para cargar dispositivos", "PartyBoost (conectar múltiples altavoces JBL)"]
             },
              {
                 "nombre": "Sonos Era 300 Altavoz inteligente", # Modelo real
                 "precio_usd": 449, "precio_gs": 449 * USD_TO_GS,
                 "colores": ["Negro", "Blanco"],
                 "caracteristicas": ["Audio espacial con Dolby Atmos", "Seis drivers posicionados para dispersión de sonido", "Control por voz (Sonos Voice, Alexa)", "WiFi y Bluetooth", "Trueplay tuning (ajuste acústico)", "Ideal para música y cine en casa (como traseros)"]
              }
         ],
        "accesorio": [
             {
                "nombre": "Apple AirPods Pro (2ª generación) con estuche USB-C",
                "precio_usd": 249, "precio_gs": 249 * USD_TO_GS,
                "colores": ["Blanco"],
                "caracteristicas": ["Cancelación Activa de Ruido mejorada", "Modo Ambiente Adaptativo", "Audio Espacial personalizado", "Chip H2", "Resistencia IP54 (auriculares y estuche)"]
            },
            {
                "nombre": "Samsung Galaxy Buds3 Pro", # Modelo hipotético
                "precio_usd": 229, "precio_gs": 229 * USD_TO_GS,
                "colores": ["Phantom Black", "Phantom Silver", "Bora Purple"],
                "caracteristicas": ["Cancelación de ruido inteligente", "Audio Hi-Fi 24 bits", "360 Audio con seguimiento de cabeza", "Diseño ergonómico mejorado", "Resistencia IPX7"]
            },
            {
                "nombre": "Anker PowerCore 20000 PD Power Bank",
                "precio_usd": 50, "precio_gs": 50 * USD_TO_GS,
                "colores": ["Negro"],
                "caracteristicas": ["Capacidad 20,000mAh", "Power Delivery (PD) 20W USB-C", "PowerIQ USB-A", "Carga hasta 2 dispositivos simultáneamente", "Compacto y fiable"]
             },
            {
                "nombre": "Logitech MX Master 3S Ratón inalámbrico",
                "precio_usd": 99, "precio_gs": 99 * USD_TO_GS,
                "colores": ["Grafito", "Gris Pálido"],
                "caracteristicas": ["Sensor óptico 8K DPI", "Clics silenciosos", "Scroll electromagnético MagSpeed", "Diseño ergonómico", " multidispositivo (hasta 3)", "USB-C carga rápida"]
             }
        ]
        # Añadir más categorías y productos aquí si es necesario
    }

# -------------------------------------------------------------------
# FUNCIONES DE APOYO
# -------------------------------------------------------------------
def generar_info_productos(productos: list) -> str:
    """Formatea la información de una lista de productos para mostrarla."""
    if not productos:
        return "No hay productos disponibles en esta categoría por el momento."

    texto = []
    # Limitar la cantidad de productos mostrados por categoría para no saturar
    MAX_PRODUCTOS_POR_CATEGORIA = 5
    for i, prod in enumerate(productos):
        if i >= MAX_PRODUCTOS_POR_CATEGORIA:
            texto.append(f"... y {len(productos) - MAX_PRODUCTOS_POR_CATEGORIA} más. Pregúntame si buscas algo específico.")
            break

        precio_gs_f = f"{prod['precio_gs']:,.0f}".replace(",", ".")
        # Incluir RAM o Tamaño si están presentes
        detalles_extra = ""
        if 'ram' in prod:
            detalles_extra += f"   🧠 RAM: {', '.join(prod['ram'])}\n"
        if 'tamaño' in prod:
             detalles_extra += f"   📏 Tamaño: {prod['tamaño'] if isinstance(prod['tamaño'], str) else ', '.join(prod['tamaño'])}\n"

        texto.append(
            f"📌 **{prod['nombre']}**\n"
            f"   💵 Precio: ${prod['precio_usd']:.2f}$ USD / ${precio_gs_f}$ Gs\n"
            f"   🎨 Colores: {', '.join(prod['colores'])}\n"
            f"   💾 Almacenamiento: {', '.join(prod.get('almacenamiento', ['N/D']))}\n"
            f"{detalles_extra}" # Añade RAM/Tamaño si existe
            f"   ⚙️ Destacado: {'; '.join(prod['caracteristicas'][:3])}..." # Muestra las 3 primeras características
        )
    return "\n\n".join(texto)


def buscar_por_caracteristicas(pregunta_lower: str, caracteristicas_solicitadas: set, catalogo: dict) -> str:
    """Busca productos que coincidan con las características solicitadas."""
    resultados_productos = []

    for categoria, productos in catalogo.items():
        for prod in productos:
            # Combina nombre, características y otros detalles en un texto para buscar
            texto_producto = f"{prod['nombre'].lower()} {' '.join(prod['caracteristicas']).lower()}"
            if 'almacenamiento' in prod: texto_producto += f" {' '.join(prod.get('almacenamiento', [])).lower()}"
            if 'colores' in prod: texto_producto += f" {' '.join(prod.get('colores', [])).lower()}"
            if 'tamaño' in prod: texto_producto += f" {prod['tamaño'] if isinstance(prod['tamaño'], str) else ' '.join(prod.get('tamaño', [])).lower()}"
            if 'ram' in prod: texto_producto += f" {' '.join(prod.get('ram', [])).lower()}"

            # Comprobar si *todas* las características solicitadas están en el texto del producto o pregunta
            # O si alguna característica clave está directamente en la pregunta
            mencionadas_en_producto = all(caract in texto_producto for caract in caracteristicas_solicitadas)
            mencionadas_en_pregunta = any(caract in pregunta_lower for caract in caracteristicas_solicitadas)

            # Priorizar si se mencionan características específicas en la pregunta
            if mencionadas_en_pregunta and any(caract in texto_producto for caract in caracteristicas_solicitadas):
                 # Podríamos refinar esto para que solo añada si la característica específica está en el producto
                if any(caract in texto_producto for caract in caracteristicas_solicitadas if caract in pregunta_lower):
                     resultados_productos.append(prod) # Añade el diccionario completo

            # Si no se menciona específicamente en la pregunta, pero todas las características están en el producto
            elif mencionadas_en_producto and not mencionadas_en_pregunta:
                 resultados_productos.append(prod) # Añade el diccionario completo

    # Eliminar duplicados si un producto coincide por varias vías
    resultados_unicos = []
    nombres_vistos = set()
    for prod in resultados_productos:
        if prod['nombre'] not in nombres_vistos:
            resultados_unicos.append(prod)
            nombres_vistos.add(prod['nombre'])

    # Formatear los resultados usando la función existente
    if resultados_unicos:
        # Aquí podrías llamar a generar_info_productos con la lista filtrada
        # return generar_info_productos(resultados_unicos[:5]) # Limitar a 5 resultados
        # O un formato más simple si prefieres:
        texto_resultados = []
        for prod in resultados_unicos[:5]: # Limitar a 5 resultados
             precio_gs_f = f"{prod['precio_gs']:,.0f}".replace(",", ".")
             categoria_prod = next((cat for cat, prods in catalogo.items() if prod in prods), "Desconocida")
             texto_resultados.append(f"• **{prod['nombre']}** ({categoria_prod.capitalize()}) - Precio: ${prod['precio_usd']:.2f}$ USD / ${precio_gs_f}$ Gs. *Características clave*: {', '.join(prod['caracteristicas'][:2])}...")
        if len(resultados_unicos) > 5:
             texto_resultados.append("... y algunos más.")
        return "\n".join(texto_resultados)

    return "" # Devuelve vacío si no hay resultados


# -------------------------------------------------------------------
# LOG
# -------------------------------------------------------------------

def guardar_prompt_log(prompt_completo):
    # Crear carpeta "log" si no existe
    os.makedirs("log", exist_ok=True)

    # Nombre del archivo basado en la fecha actual
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    archivo = f"log/promt_log_{fecha}.txt"

    # Agregar contenido con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"\n\n--- PROMPT GENERADO PARA EL MODELO ({timestamp}) ---\n"
    log_content += prompt_completo
    log_content += "\n--- FIN DEL PROMPT ---\n"

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(log_content)