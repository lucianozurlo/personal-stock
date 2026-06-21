# ComuStock — Agente de chat

Chatbot de ComuStock, el repositorio interno de activos de marca de Personal Argentina. El agente responde preguntas sobre recursos disponibles (logos, isotipos, templates, audiovisuales, tipografías) a través de una interfaz de chat embebida, con memoria conversacional persistente y búsqueda semántica sobre el catálogo.

## Qué hace

- Recibe mensajes del usuario vía chat.
- Busca contexto relevante en una base RAG (JSONL con los chunks del catálogo de ComuStock).
- Mantiene estado conversacional entre turnos: marca activa, tipo de recurso, color, formato, fondo.
- Responde con Gemini 2.5 Flash (fallback a Groq llama-3.3-70b si Gemini falla).
- Devuelve tarjetas HTML con links de descarga directos cuando el pedido está completamente filtrado.
- Deriva a `equipocomunicacioninterna@personal.com.ar` solo cuando no hay ninguna coincidencia en el catálogo.

## Stack

| Componente | Tecnología |
|---|---|
| Frontend | HTML + CSS + JS vanilla |
| Orquestación | n8n (self-hosted, host) |
| RAG | JSONL servido como estático |
| Memoria conversacional | PostgreSQL 16 |
| Web / RAG server | nginx (Docker) |
| LLM principal | Gemini 2.5 Flash |
| LLM fallback | Groq llama-3.3-70b |

## Estructura

```
cs-chat-rag/
├── prompt-comustock.html          # frontend del chat
├── css/styles.css
├── js/                            # módulos del frontend
│   ├── config.js                  # URL del webhook, gestión de conversationId
│   ├── api.js                     # llamadas al webhook
│   ├── composer.js                # input y envío de mensajes
│   ├── state.js
│   ├── ui.js
│   └── main.js
├── rag/
│   └── comustock_rag_chunks_html_compacto_v2_2026-04-17.jsonl  # base RAG
├── n8n/
│   ├── workflow/                  # workflow principal de n8n
│   ├── sql/                       # scripts de inicialización de PostgreSQL
│   ├── examples/                  # payload de ejemplo para el webhook
│   └── docs/                      # documentación técnica y reportes
├── docker-compose.yml             # Postgres + nginx
└── check_env.sh                   # verificación del entorno
```

## Cómo ejecutarlo

### Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop) corriendo
- Node.js 18+
- Credencial de [Gemini](https://aistudio.google.com/apikey) y de [Groq](https://console.groq.com/keys)

### Arrancar

**1. Abrir Docker Desktop** y esperar a que la ballena en la barra de menú esté estática.

**2. Infraestructura** (Postgres + nginx):
```bash
docker compose up -d
docker compose ps   # postgres: healthy, web: running
```

**3. n8n** (en una terminal aparte):
```bash
npx n8n
```
Esperar hasta ver `Editor is now accessible via: http://localhost:5678/`

**4. Importar el workflow** en n8n:
- Workflows → ⋯ → Import from File
- Elegir `n8n/workflow/Comustock_Etapa_2_4_Chat_RAG_DB_memory_FIX_estado.json`

**5. Configurar credenciales** en los nodos:
- `Google Gemini Chat Model` → API key de Gemini
- `Groq Chat Model — Fallback` → API key de Groq
- Los 6 nodos Postgres → host `localhost`, puerto `5432`, DB `comustock`, user `comustock`, pass `comustock_dev`, SSL deshabilitado

**6. Activar el workflow** (toggle Active → ON).

**7. Abrir el chat:**
```
http://localhost:3000/prompt-comustock.html
```

### Verificar el entorno
```bash
./check_env.sh
```

### Detener
```bash
# Ctrl+C en la terminal de n8n
docker compose down
```

## Webhook

El frontend llama a:
```
POST http://localhost:5678/webhook/comustock-chat
Content-Type: application/json

{
  "conversationId": "conv-xxxxx",
  "userId": "benja",
  "query": "necesito el logo de Flow"
}
```

Respuesta:
```json
{
  "output": "<p>...</p>",
  "html_render": true
}
```
