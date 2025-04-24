

def pregunta_con_contexto(pregunta, historial) -> str:
    """
    Crea un prompt optimizado para un asistente virtual especializado en ventas,
    siguiendo las mejores prácticas de contexto, claridad y tono persuasivo y amable.
    """
    historial = f"\nHistorial de la conversación:\n{historial}" if historial else "No hay historial disponible."

    condiciones_dinamicas = generar_condiciones_dinamicas(pregunta)
    if condiciones_dinamicas.strip():
        condiciones_dinamicas = "\n🧠 **Conversación dinámica generada:**\n" + condiciones_dinamicas


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
   - Ofrecé recomendaciones personalizadas según lo que el cliente necesita o está buscando.

3. **Proceso de Compra:**
   - Guiá al cliente en los pasos para comprar: cómo hacerlo, qué opciones tiene y cómo confirmar su compra.
   - Si el cliente tiene dificultades, resolvélas de forma simple y directa.

4. **Promociones y Descuentos:**
   - Informá sobre cualquier promoción activa, cupones, combos o descuentos.
   - Aprovechá las oportunidades para sugerir productos complementarios o de mayor valor.

5. **Atención Post-Venta:**
   - Informá sobre tiempos de entrega, seguimiento de pedidos, cambios o devoluciones si lo solicita.
   - Consultá si quedó conforme con su compra y ofrecé asistencia adicional si es necesario.

6. **Escalación si es Necesario:**
   - Si el cliente tiene una consulta muy específica o requiere atención humana, informá que vas a escalar su caso y derivarlo al equipo adecuado.

7. **Detecta emociones o indecisión:**
   - Si notas que el cliente está dudando o frustrado (palabras como "no sé", "caro", "duda", "complicado"), tranquilízalo y ofrécele alternativas o beneficios adicionales.

8. **Al finalizar, pide feedback:**
   - Pregunta amablemente si la atención fue útil y si hay algo más que puedas mejorar.
   


{condiciones_dinamicas}


{historial}


Pregunta actual:
{pregunta}

Notas adicionales:
- Si el cliente está listo para comprar, guiá el proceso de cierre de venta.
- Si el cliente no sabe qué quiere, ayudalo a decidir con preguntas breves o sugerencias.
- Siempre agradecé su interés y ofrecé ayuda adicional antes de terminar.
- Si el cliente ya compró, consultá si quedó conforme y ofrecé productos relacionados o soporte.

**Max_token:**
- 200
    """
    return prompt.strip()







# Bloques de palabras clave (podrían estar en un archivo aparte como constants.py)
PALABRAS_CLAVE = {
    "promocion": {"promoción", "oferta", "ofertas", "descuento", "cupón", "rebaja", "promo"},
    "politicas": {"garantía", "devolución", "reembolso", "cambio", "entrega", "envío", "política"},
    "precio": {"precio", "cuánto cuesta", "valor", "costó", "cuanto sale", "cotización"},
    "caracteristicas": {"cámara", "batería", "almacenamiento", "color", "pantalla", "ram", "procesador", "tamaño"},
    "categorias": {"celular", "celulares",  "notebook", "tablet", "accesorio", "smartwatch", "consola", "tv", "audio"}
}
def generar_condiciones_dinamicas(pregunta: str) -> str:
    condiciones = []
    pregunta_lower = pregunta.lower()
    
    # 1. Detección más eficiente usando conjuntos
    palabras_en_pregunta = set(pregunta_lower.split())
    
    # 2. Manejo de promociones optimizado
    if PALABRAS_CLAVE["promocion"] & palabras_en_pregunta:
        promos = obtener_promociones_actuales()
        promos_texto = "\n".join([
            f"• 🎁 {p['nombre']}: {p['detalle']}" 
            for p in promos
        ])
        condiciones.append(f"📢 **Promociones vigentes:**\n{promos_texto}")
    
    # 3. Manejo de políticas con detección mejorada
    if PALABRAS_CLAVE["politicas"] & palabras_en_pregunta:
        politicas = obtener_politicas_completas()
        politicas_texto = "\n".join([
            f"• 🔧 {key.capitalize()}: {value}" 
            for key, value in politicas.items()
        ])
        condiciones.append(f"📜 **Políticas aplicables:**\n{politicas_texto}")
    
    # 4. Búsqueda por categoría optimizada
    categorias_solicitadas = PALABRAS_CLAVE["categorias"] & palabras_en_pregunta
    if categorias_solicitadas:
        catalogo = obtener_catalogo_completo()
        for categoria in categorias_solicitadas:
            if categoria in catalogo:
                productos_texto = generar_info_productos(catalogo[categoria])
                condiciones.append(f"🛍️ **Productos en {categoria.capitalize()}:**\n{productos_texto}")
    
    # 5. Búsqueda por precio más precisa
    if PALABRAS_CLAVE["precio"] & palabras_en_pregunta and categorias_solicitadas:
        catalogo = obtener_catalogo_completo()
        for categoria in categorias_solicitadas:
            if categoria in catalogo:
                precios_texto = "\n".join([
                    f"• {prod['nombre']}: {prod['precio_usd']} USD / {prod['precio_gs']:,.0f} Gs"
                    for prod in catalogo[categoria]
                ])
                condiciones.append(f"💰 **Precios en {categoria.capitalize()}:**\n{precios_texto}")
    
    # 6. Búsqueda por características optimizada
    caracteristicas_solicitadas = PALABRAS_CLAVE["caracteristicas"] & palabras_en_pregunta
    if caracteristicas_solicitadas:
        resultados = buscar_por_caracteristicas(pregunta_lower, caracteristicas_solicitadas)
        if resultados:
            condiciones.append(f"🔍 **Productos relacionados con {', '.join(caracteristicas_solicitadas)}:**\n{resultados}")
    
    # 7. Búsqueda de productos específicos
    if any(palabra in pregunta_lower for palabra in ["producto", "productos"]):
        catalogo = obtener_catalogo_completo()
        productos_texto = []
        for categoria, productos in catalogo.items():
            for prod in productos[:5]:  # Limitar la cantidad de productos
                productos_texto.append(f"• {prod['nombre']}: {prod['detalle']}")
        
        if productos_texto:
            condiciones.append(f"🛍️ **Algunos productos disponibles:**\n" + "\n".join(productos_texto))
    
    # 8. Respuesta específica de un producto
    if any(palabra in pregunta_lower for palabra in ["iphone", "samsung", "macbook", "ipad"]):
        catalogo = obtener_catalogo_completo()
        for categoria, productos in catalogo.items():
            for prod in productos:
                if prod['nombre'].lower() in pregunta_lower:
                    producto_detalle = f"📌 **{prod['nombre']}**\n" \
                                       f"💵 Precio: {prod['precio_usd']} USD / {prod['precio_gs']:,.0f} Gs\n" \
                                       f"🎨 Colores: {', '.join(prod['colores'])}\n" \
                                       f"💾 Almacenamiento: {', '.join(prod.get('almacenamiento', ['N/A']))}\n" \
                                       f"⚙️ Características principales: {', '.join(prod['caracteristicas'][:3])}"
                    condiciones.append(f"🛍️ **Detalles de {prod['nombre']}**:\n{producto_detalle}")
    
    return "\n🌟 **Información Relevante:**\n" + "\n\n".join(condiciones) if condiciones else ""

    


# -------------------------------------------------------------------
# MÓDULO DE DATOS (puede estar en otro archivo, ej: datos.py)
# -------------------------------------------------------------------

def obtener_politicas_completas():
    return {
        "garantia": "12 meses contra defectos de fábrica (24 meses para notebooks)",
        "devolucion": "30 días para cambios (producto debe estar sin uso y en empaque original)",
        "reembolso": "15 días para devoluciones (requiere factura y formulario completado)",
        "entrega": "Envío gratis en Asunción para compras >1.000.000 Gs. Tiempo: 24-72 horas hábiles",
        "instalación": "Servicio gratuito de instalación/configuración para productos seleccionados"
    }

def obtener_promociones_actuales():
    return [
        {
            "nombre": "Super Descuento Tecnológico",
            "detalle": "Hasta 40% off en celulares y tablets de última generación",
            "valido_hasta": "30/11/2023"
        },
        {
            "nombre": "Combo Gamer",
            "detalle": "Lleva una notebook gamer + auriculares + mouse y ahorra 1.200.000 Gs",
            "valido_hasta": "15/12/2023"
        },
        {
            "nombre": "Días sin IVA",
            "detalle": "10% adicional de descuento en toda la tienda este fin de semana",
            "valido_hasta": "10/12/2023"
        }
    ]

def obtener_catalogo_completo():
    USD_TO_GS = 7300  # Tipo de cambio aproximado
    
    return {
        "celular": [
            {
                "nombre": "iPhone 15 Pro Max",
                "precio_usd": 1099,
                "precio_gs": 1099 * USD_TO_GS,
                "colores": ["Negro espacial", "Blanco estelar", "Azul sierra"],
                "almacenamiento": ["128GB", "256GB", "512GB"],
                "caracteristicas": ["Pantalla Super Retina XDR", "Chip A17 Pro", "Cámara triple 48MP"]
            },
            {
                "nombre": "Samsung Galaxy S23 Ultra",
                "precio_usd": 1199,
                "precio_gs": 1199 * USD_TO_GS,
                "colores": ["Negro", "Verde", "Crema"],
                "almacenamiento": ["256GB", "512GB", "1TB"],
                "caracteristicas": ["Pantalla Dynamic AMOLED", "S-Pen incluido", "Cámara 200MP"]
            }
        ],
        "notebook": [
            {
                "nombre": "MacBook Pro 14\" M2",
                "precio_usd": 1999,
                "precio_gs": 1999 * USD_TO_GS,
                "colores": ["Plateado", "Gris espacial"],
                "almacenamiento": ["512GB", "1TB"],
                "caracteristicas": ["Chip M2 Pro", "Pantalla Liquid Retina", "18h batería"]
            }
        ],
        "tablet": [
            {
                "nombre": "iPad Air 2023",
                "precio_usd": 599,
                "precio_gs": 599 * USD_TO_GS,
                "colores": ["Azul", "Rosa", "Plateado"],
                "almacenamiento": ["64GB", "256GB"],
                "caracteristicas": ["Chip M1", "Pantalla Liquid Retina", "Compatibilidad Apple Pencil"]
            }
        ],
        "accesorio": [
            {
                "nombre": "AirPods Pro 2da Gen",
                "precio_usd": 249,
                "precio_gs": 249 * USD_TO_GS,
                "colores": ["Blanco"],
                "caracteristicas": ["Cancelación de ruido", "Audio espacial", "Carga MagSafe"]
            }
        ]
    }

# -------------------------------------------------------------------
# FUNCIONES DE APOYO
# -------------------------------------------------------------------

def generar_info_productos(productos):
    texto = []
    for prod in productos:
        precio_gs = f"{prod['precio_gs']:,.0f}".replace(",", ".")
        texto.append(
            f"📌 **{prod['nombre']}**\n"
            f"   💵 Precio: {prod['precio_usd']} USD / {precio_gs} Gs\n"
            f"   🎨 Colores: {', '.join(prod['colores'])}\n"
            f"   💾 Almacenamiento: {', '.join(prod.get('almacenamiento', ['N/A']))}\n"
            f"   ⚙️ Características principales: {', '.join(prod['caracteristicas'][:3])}"
        )
    return "\n\n".join(texto)

def buscar_por_caracteristicas(pregunta):
    catalogo = obtener_catalogo_completo()
    resultados = []
    
    for categoria, productos in catalogo.items():
        for prod in productos:
            # Búsqueda en características
            if any(caract in " ".join(prod['caracteristicas']).lower() for caract in ["cámara", "batería", "pantalla"] if caract in pregunta):
                resultados.append(f"{prod['nombre']} ({categoria})")
            
            # Búsqueda por color
            if "color" in pregunta and any(color.lower() in pregunta for color in prod['colores']):
                resultados.append(f"{prod['nombre']} en {', '.join([c for c in prod['colores'] if c.lower() in pregunta])}")
    
    return "\n".join(resultados[:5]) if resultados else ""