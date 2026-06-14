# sistema-automatizacion-ia-hotel

¡Qué gran idea, Kobayashi! Incluir los errores técnicos que superamos en el camino dentro de la documentación es lo que diferencia a un desarrollador novato de uno profesional. Esto demuestra que realmente entiendes lo que construiste y que sabes cómo solucionar problemas en el mundo real. Al profesor le va a encantar este nivel de autocrítica y honestidad técnica.

Aquí tienes la Guía Completa de Desarrollo de tu Proyecto lista para copiar, pegar y lucirte en el README.md de tu repositorio de GitHub:

🏨 Sistema de Automatización con IA para Gestión de Huéspedes - Hotel Luxury
Este repositorio contiene el código fuente, el flujo de automatización y la documentación técnica de un ecosistema inteligente diseñado para gestionar solicitudes, reseñas y clasificar clientes de un hotel de lujo utilizando Inteligencia Artificial Autónoma y agentes basados en funciones (Tools Agent).

🛠️ Arquitectura del Sistema (Niveles del Proyecto)
El desarrollo del proyecto se dividió en fases incrementales de complejidad, logrando un sistema automatizado robusto y capaz de tomar decisiones en tiempo real.

🔹 Nivel 1: Automatización Lineal y Filtrado de Reseñas
Objetivo: Capturar la información de un formulario de satisfacción de clientes y filtrarla según su calificación.

Flujo: El huésped llena un formulario web en n8n ingresando su nombre y reseña. El sistema evalúa la reseña y redirige el flujo de datos según el sentimiento detectado para optimizar los tiempos de respuesta del equipo de atención al cliente.

🔹 Nivel 2: Agente de IA Autónomo con Herramientas Personalizadas
Objetivo: Crear un agente con capacidad de toma de decisiones utilizando modelos de lenguaje avanzados.

Flujo: Se integró un AI Agent conectado a un modelo de lenguaje de Groq (usando la API para procesamiento rápido). El agente tiene acceso a una herramienta de código personalizada (Code Tool) que simula una base de datos interna de clientes del hotel en formato JavaScript.

Lógica de Negocio: El agente busca de forma autónoma el estatus del cliente en la base de datos simulada. Al detectar que un huésped con estatus VIP (como Marta Gómez) deja una reseña negativa o experimenta un fallo en la habitación, el agente toma el control, redacta una compensación personalizada, envía un correo electrónico formal a través de Gmail de manera automatizada y extrae la información estructurada mediante un Information Extractor para cerrar el caso.

🚀 Guía de Replicación e Instalación
Para montar este flujo en tu propia instancia de n8n, sigue estos pasos:

Clonar el Flujo: Descarga el archivo .json de este repositorio. En tu lienzo de n8n, haz clic en el menú de opciones (tres puntos ...) e impórtalo seleccionando Import from file.

Configurar Credenciales:

Groq API: Genera una clave API gratuita en la consola de Groq y conéctala en el nodo del modelo de lenguaje.

Gmail: Configura la credencial de Google de tipo OAuth2 en el nodo de Gmail para permitir el envío automático de correos electrónicos.

Configurar la Base de Datos Simulada (Code Tool): Asegúrate de que el nodo de código contenga la estructura JSON simulada que expone las propiedades del huésped (nombre, habitación, noches restantes y estatus).

⚠️ Bitácora de Errores y Soluciones (Troubleshooting)
Si vas a replicar este proyecto, es muy probable que te enfrentes a los mismos retos técnicos que nosotros superamos. Aquí tienes las soluciones directas:

❌ Error 1: "$helpers is not defined" en el nodo de código
Problema detectado: Al intentar automatizar el envío de correos utilizando funciones internas avanzadas escribiendo await $helpers.sendEmail(...) dentro de un bloque de código personalizado (Code Tool), el flujo se detenía lanzando un error fatal de definición de objeto. Esto ocurre porque las versiones modernas de n8n bloquean la inyección de estas librerías por motivos de seguridad o requieren variables de entorno específicas desactivadas por defecto.

Solución aplicada: Se removió la lógica de envío de correos del código personalizado de JavaScript. En su lugar, se adoptó un enfoque puramente modular y visual, delegando la tarea al nodo nativo de Gmail (Send a message) en el lienzo general. El nodo Code Tool se limpió para que su única función sea actuar de manera síncrona como la base de datos del hotel, entregando propiedades limpias (nombre, estatus_cliente: "VIP") directamente al Agente de IA.

❌ Error 2: Complicación en la Inserción de Memoria RAG (Fase Vectorial)
Problema detectado: Al intentar escalar el proyecto a un Nivel 3 para que la IA consultara un manual de políticas en formato de texto plano (.txt), se generaron conflictos de cables en la interfaz debido a cambios drásticos de estructura en las versiones de n8n. Configurar el nodo Simple Vector Store en modo Insert abría el puerto de entrada para el cargador de datos (Default Data Loader), pero eliminaba los puertos de conexión hacia la herramienta del agente; mientras que configurarlo en modo Retrieve desconectaba el cargador. Adicionalmente, el cargador requería forzosamente la inyección de un tipo de dato binario (Binary) mediante un nodo externo de lectura de disco duro para poder subir archivos locales.

Solución / Decisión Estratégica: Debido a la alta complejidad, la redundancia de datos por cada ciclo de ejecución del formulario y las restricciones estrictas de la interfaz de LangChain en n8n, se tomó la decisión arquitectónica de mantener el sistema consolidado en el Nivel 2. Esto garantizó un flujo limpio, completamente funcional, de alto rendimiento y libre de advertencias rojas en producción.
