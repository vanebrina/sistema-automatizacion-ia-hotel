# Flujos n8n — Nivel 1 (referencia)

Esta carpeta contiene los flujos originales de **n8n** que sirvieron de base para la
reimplementación en LangChain (Nivel 2). Se incluyen como evidencia y para permitir la
comparación N8n vs. LangChain (ver el README principal).

| Archivo | Descripción |
|---|---|
| `n8n_nivel1.json` | Flujo lineal: formulario → análisis de sentimiento → Google Sheets → enrutado (IF) → alerta Telegram. |
| `n8n_nivel2.json` | Agente autónomo: añade el `Code Tool` (BD simulada del hotel), uso de herramientas por el agente y correo de compensación (Gmail). |

## Cómo importarlos en n8n
1. Abre tu instancia de n8n.
2. Menú **⋮ → Import from File**.
3. Selecciona el `.json` deseado.
4. Configura las credenciales (Groq, Gmail OAuth2, Google Sheets OAuth2, Telegram).
