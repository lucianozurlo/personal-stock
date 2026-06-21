# Brief ordenado para Kiro — Personal Stock

**Proyecto:** Personal Stock  
**Objetivo del documento:** ordenar el brief fusionado para que Kiro pueda entender claramente qué debe construir, qué archivos tendrá disponibles, cómo se organiza la arquitectura, cómo funciona el orquestador, qué agentes forman parte del MVP 1 y qué procesos no deben quedar ambiguos.

---

# Nota de naming y herencia

El nombre definitivo del proyecto es **Personal Stock**.

Todo lo que en archivos, carpetas o documentación anterior figure como **Comustock** pertenece a un proyecto anterior. En este brief, Comustock no debe interpretarse como nombre del producto actual, marca vigente ni módulo principal. Debe interpretarse únicamente como fuente heredada de contenidos, sitemap, archivos, recursos y referencias que se incorporarán o simularán dentro de Personal Stock.

Si Kiro encuentra textos, variables, carpetas o comentarios con el nombre Comustock, no debe renombrar automáticamente archivos físicos si eso rompe rutas existentes, pero sí debe evitar usar Comustock como nombre visible del nuevo producto. En la interfaz visible al usuario debe decir Personal Stock.


# 1. Archivos e insumos disponibles para Kiro

Kiro tendrá a disposición los siguientes archivos y carpetas. Antes de diseñar o implementar, deberá inspeccionarlos y usarlos como fuente de verdad cuando corresponda.

```txt
cs-chat-rag
comustock-base
mails
  attachments
  images
  output
    contenido_md
    lotes
    relevamiento_enriquecido.json
    relevamiento_final.json
    relevamiento.csv
    relevamiento.json
  workflows n8n
  enriquecer.py
  unificar.py

templates
  home.html
  login.html
  personal-stock-logo.svg
  personal-stock-logo-light.svg
  otros templates HTML que se entreguen
brand_key_voz_tono_personal.md
brief_insumos_kiro_appweb_comustock.md
chatbot-1.png
chatbot-2.png
comustock_base.csv
ESTRUCTURA_DATASET.md
plan de agentes.csv
resumen proyecto previo (bot).md
screencapture-m3-material-1.png
screencapture-m3-material-2.png
```

## 1.1 Uso esperado de cada insumo

### `cs-chat-rag`

Es el proyecto base / chatbot previo. Corresponde al repo:

```txt
https://github.com/lucianozurlo/cs-chat-rag.git
```

Debe ser inspeccionado antes de modificar cualquier cosa. Kiro no debe inventar estructura, endpoints, nodos, archivos ni integraciones. Debe revisar lo existente y continuar desde esa base.

### `resumen proyecto previo (bot).md`

Debe usarse para entender qué hace el bot anterior, cómo está pensado y qué partes conviene reutilizar o adaptar.

### `chatbot-1.png` y `chatbot-2.png`

Sirven para comprender visualmente el chatbot base/proyecto previo.

### `templates`

La carpeta `templates` contiene los templates HTML básicos para el inicio del MVP:

```txt
templates/home.html
templates/login.html
templates/personal-stock-logo.svg
templates/personal-stock-logo-light.svg
```

`home.html` y `login.html` son la base visual y estructural inicial del MVP. Kiro debe integrarlos a Django y al frontend sin rediseñarlos desde cero.

El logo principal de Personal Stock está en:

```txt
templates/personal-stock-logo.svg
```

La versión para cuando el template haga switch a modo light está en:

```txt
templates/personal-stock-logo-light.svg
```

Todo contenido o bloque de `home.html` que no sea necesario para este inicio deberá quedar simulado, oculto, mockeado o preparado para una próxima evolución del desarrollo. No debe eliminarse sin criterio si sirve como estructura futura.



### `screencapture-m3-material-1.png` y `screencapture-m3-material-2.png`

Son referencias secundarias de interfaz. Pueden ayudar a definir detalles visuales, cards, componentes o estructura, pero no reemplazan la referencia principal de los templates HTML entregados.

### `comustock_base.csv`

Es el sitemap o estructura del proyecto anterior Comustock. Debe usarse para poblar, simular o estructurar las secciones heredadas dentro de Personal Stock.

### `comustock-base`

Contiene el contenido del proyecto anterior Comustock. Ese contenido será parte del nuevo proyecto Personal Stock como contenido heredado.

Comustock pertenece a un proyecto anterior. Todo lo que diga Comustock debe entenderse únicamente como contenido heredado, sitemap anterior, recursos previos o fuente de información para migrar/simular dentro de Personal Stock.

### `mails`

Contiene el relevamiento histórico de comunicaciones internas. Es la base del agente de historial de mails/RAG.

Dentro de `mails` están:

```txt
attachments
images
output/contenido_md
output/lotes
output/relevamiento_enriquecido.json
output/relevamiento_final.json
output/relevamiento.csv
output/relevamiento.json
workflows n8n
enriquecer.py
unificar.py
```

La fuente final principal para consultas será:

```txt
mails/output/relevamiento_enriquecido.json
```

Los contenidos completos de links y adjuntos estarán en:

```txt
mails/output/contenido_md
```

Las imágenes estarán en:

```txt
mails/images
```

Los adjuntos estarán en:

```txt
mails/attachments
```

### `ESTRUCTURA_DATASET.md`

Es la fuente de verdad de la estructura del dataset. No debe tratarse ningún campo ya documentado ahí como pendiente o futuro.

### `brand_key_voz_tono_personal.md`

Es el Manual de Voz y Tono / Brand Key de Personal. Debe usarse para el Agente Redactor CI, QA Editorial, revisión de tono, generación de copies y validación de estilo.

### `plan de agentes.csv`

Puede usarse como referencia general, pero para MVP 1 Kiro debe basarse en los agentes definidos en este brief. No debe intentar construir todos los agentes del plan si exceden el alcance del MVP 1.

### `brief_insumos_kiro_appweb_comustock.md`

Es un brief anterior de insumos. Debe tomarse como antecedente, no como fuente final si contradice este documento.

---

# 2. Nombre del proyecto y alcance general

El proyecto se llamará:

```txt
Personal Stock
```

El proyecto ya no se llamará Comustock.

Comustock pertenece a un proyecto anterior y debe entenderse únicamente como:

```txt
contenido heredado
sitio anterior
sitemap base
recursos existentes
material que se migrará o simulará dentro de Personal Stock
```

Personal Stock ya tiene logo dentro de la carpeta `templates`. Para MVP 1, Kiro debe usar `templates/personal-stock-logo.svg` como logo principal y `templates/personal-stock-logo-light.svg` cuando el template cambie a versión light. No debe usar logos de Comustock ni placeholders si los SVG de Personal Stock están disponibles.

Personal Stock será una app web compleja que funcionará principalmente como:

```txt
sitio web
bot
asistente
agente
plataforma de apoyo a InternalComms y Cultura de Personal
```

El foco del MVP 1 estará en:

```txt
Home con prompt conversacional
interfaz basada en los templates HTML entregados
orquestador principal en n8n
agentes principales del MVP 1
consulta histórica de mails vía RAG
Trigger Comunicaciones para e-mail
memoria por usuario
permisos por perfil
contenido heredado del proyecto anterior Comustock
tablero de métricas
página de acciones
roadmap de eventos y comunicaciones
```

El MVP 1 correrá localmente. No debe asumirse preparado para 20.000 usuarios, aunque la arquitectura debe dejar claro qué se deberá modificar para escalar a ese volumen en otro MVP.

---

# 3. Forma de trabajo esperada en Kiro

Kiro debe trabajar con una estrategia eficiente para evitar sobrecargar una sola generación y para reducir errores de implementación.

El orden esperado es:

```txt
1. Inspeccionar los archivos y carpetas disponibles.
2. Revisar primero `cs-chat-rag`, `templates/home.html`, `templates/login.html`, `resumen proyecto previo (bot).md`, `ESTRUCTURA_DATASET.md` y el contenido de `mails`.
3. Identificar qué ya existe, qué se puede reutilizar y qué debe crearse desde cero.
4. Generar spec plan.
5. Generar requisitos.
6. Generar diseño técnico y funcional.
7. Dividir la implementación en tareas pequeñas, verificables y secuenciales.
8. Implementar tarea por tarea, validando cada avance antes de continuar.
9. Documentar decisiones, limitaciones, pendientes y próximos MVPs.
```

Para hacer la generación más eficiente, Kiro debe evitar intentar construir todo el sistema en una sola pasada. Debe trabajar por bloques funcionales:

```txt
Bloque 1: revisión del repo base y templates.
Bloque 2: integración de login.html y home.html en Django.
Bloque 3: usuarios demo, perfiles y sesión.
Bloque 4: Home con saludo, logo, menú, prompt y carousel.
Bloque 5: contrato del orquestador y conexión n8n.
Bloque 6: agentes MVP 1 con workflows, mocks o contratos según corresponda.
Bloque 7: dataset/RAG con permisos.
Bloque 8: Trigger Comunicaciones.
Bloque 9: métricas, acciones y trazabilidad.
Bloque 10: documentación de instalación y límites.
```

Kiro no debe comenzar implementando directamente sin antes generar el spec plan, los requisitos y el diseño. Tampoco debe mezclar demasiadas tareas en un único paso. Si una parte no puede completarse en MVP 1, debe dejarla marcada como simulada, preparada o pendiente para MVP posterior.

---


# 4. Fuente visual principal: templates HTML

La fuente visual principal de Personal Stock será la carpeta:

```txt
templates
```

Los templates básicos para este inicio son:

```txt
templates/login.html
templates/home.html
```

Kiro deberá tomar esos dos templates como fuente de verdad visual y estructural para el MVP inicial. Deberá integrarlos en Django, conectar datos dinámicos y adaptar lo necesario para login, sesión, usuario activo, prompt, menú, carousel y orquestador, pero no deberá rediseñarlos desde cero.

El logo principal y su versión light están en:

```txt
templates/personal-stock-logo.svg
templates/personal-stock-logo-light.svg
```

Todo contenido de `home.html` que no sea necesario para este inicio deberá quedar simulado, mockeado o preparado para una próxima evolución del desarrollo. El objetivo del MVP inicial es que login y home funcionen correctamente. El resto de los espacios quedará preparado para una evolución posterior.

---


# 5. Arquitectura general del MVP inicial

Personal Stock tendrá una arquitectura preparada para crecer, pero el desarrollo inicial se basará operativamente solo en:

```txt
login
home
prompt
orquestador
usuarios demo
sesión
menú lateral
carousel
trazabilidad básica
acciones/métricas básicas
```

Para este inicio, las piezas visuales obligatorias son:

```txt
templates/login.html
templates/home.html
```

El resto de los espacios del sitio, como Stock, Templates, Mi firma, Toolbox y Roadmap, deberán quedar preparados a nivel navegación, rutas, estructura y placeholders, pero estarán operativos en un desarrollo posterior.

El sistema debe diferenciar claramente:

```txt
Aplicación web Personal Stock
Backend Django
Frontend basado en templates HTML
Login
Home
n8n
Orquestador principal
Agentes independientes coordinados por el orquestador
Dataset histórico
Contenido heredado del proyecto anterior Comustock
Memoria
Métricas
```

---


# 6. Orquestador principal y organización de agentes

El orquestador principal es el centro del sistema conversacional.

Debe entenderse así:

```txt
Prompt de Home
↓
Orquestador principal en n8n
↓
Clasificación de intención
↓
Validación de usuario, perfil y permisos
↓
Selección del agente correspondiente
↓
Llamada al workflow del agente
↓
Respuesta al usuario
↓
Registro en trazabilidad, acciones y métricas
```

El orquestador **contiene funcionalmente al resto de los agentes** en el sentido de que es el punto de entrada, decisión y coordinación. Los agentes no se activan por separado desde la interfaz sin pasar por una lógica de orquestación, salvo que una acción interna o shortcut del carousel dispare una intención ya preclasificada.

Cada agente tendrá su propio workflow independiente en n8n, pero el orquestador será quien determine cuándo llamarlo.

Los agentes obligatorios del MVP 1 son:

```txt
Orquestador principal
Agente de historial de mails / RAG
Trigger Comunicaciones
Agente Generador de propuestas creativas
Agente Redactor CI
Agente QA Editorial
Agente Cumplimiento y Riesgo
Roadmap Eventos
```

El orquestador debe poder responder con el LLM base si no corresponde llamar a un agente especializado.

Ejemplo:

```txt
Usuario: ¿Cuál es la capital de Paraguay?
Resultado esperado: respuesta general del LLM base.
```

Ejemplo con agente:

```txt
Usuario: Necesito generar un plan de comunicación.
Resultado esperado: derivación al agente Trigger Comunicaciones.
```


---

# 7. Reglas de orquestación

El orquestador debe clasificar la intención antes de responder.

Categorías iniciales de intención:

```txt
consulta_general
consulta_historial_mails
generar_plan_comunicacion
crear_copy_email
revisar_qa_editorial
validar_cumplimiento
pedir_ideas_creativas
consultar_contenido_personalstock
consultar_roadmap
accion_perfil
fallback
```

Reglas iniciales:

```txt
Si el usuario pide explícitamente buscar, comparar, recordar, consultar o analizar mails históricos dentro del bot, derivar al Agente de historial de mails/RAG. Este agente no debe sugerirse proactivamente como atajo comercial ni como recomendación automática; solo debe activarse ante una consulta explícita del usuario.

Si el usuario pide crear una comunicación, plan de comunicación, campaña o envío, derivar a Trigger Comunicaciones.

Si el usuario pide solo copy para e-mail, puede derivar a Redactor CI, pero si falta brief debe pasar primero por Trigger Comunicaciones o pedir datos mínimos.

Si el usuario pide revisar tono, marca, claridad u ortografía, derivar a QA Editorial.

Si el usuario pide validar riesgos, datos sensibles, PII o cumplimiento, derivar a Cumplimiento y Riesgo.

Si el usuario pide ideas, enfoques o conceptos creativos, derivar al Generador de propuestas creativas.

Si el usuario pregunta por templates, manuales, logos o recursos del sitio, consultar contenido heredado del proyecto anterior Comustock dentro de Personal Stock.

Si no hay agente aplicable, responder con LLM base.
```

Si el orquestador no puede determinar el agente correcto, debe pedir una aclaración breve.

Ejemplo:

```txt
Puedo ayudarte de dos formas: iniciar un nuevo plan de comunicación o resolver una consulta puntual desde el bot. ¿Cuál querés hacer?
```

No debe simular que una acción fue realizada si no se ejecutó correctamente.

---

# 8. Contrato común de agentes

Todos los workflows de n8n y agentes deben manejar una entrada y salida común para evitar integraciones frágiles.

Entrada mínima:

```json
{
  "request_id": "uuid",
  "conversation_id": "uuid",
  "user": {
    "id": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "profile": "Administrador | Usuario IC | Heavy user | Macro | Usuario",
    "roles": ["string"],
    "areas": ["string"],
    "memory_enabled": true
  },
  "message": "texto ingresado por el usuario",
  "source": "home_prompt | carousel_shortcut | workflow_action | profile_action",
  "context": {
    "project_id": "opcional",
    "agent_id": "opcional",
    "previous_state": "opcional"
  }
}
```

Salida mínima:

```json
{
  "request_id": "uuid",
  "agent": "nombre_del_agente",
  "status": "success | needs_input | pending_approval | blocked | error",
  "message": "respuesta visible para el usuario",
  "data": {},
  "actions": [],
  "next_step": "string opcional",
  "trace": {
    "workflow_id": "string",
    "run_id": "string",
    "started_at": "datetime",
    "finished_at": "datetime"
  }
}
```

Si el agente necesita más información, debe devolver `needs_input`. Si no puede avanzar por permisos, debe devolver `blocked`. Si falla una integración, debe devolver `error`.

---

# 9. Estados generales de ejecución

Toda ejecución de agente o workflow debe tener estado.

Estados mínimos:

```txt
created
running
needs_input
waiting_human
pending_approval
approved
rejected
blocked_by_permissions
blocked_by_compliance
failed
cancelled
completed
```

Estos estados deben alimentar:

```txt
página de acciones
tablero de métricas
trazabilidad del proyecto
historial de conversación
```

---

# 10. Trazabilidad

Todo proceso iniciado desde el prompt debe dejar trazabilidad.

Debe registrarse:

```txt
usuario que inició
fecha y hora
mensaje original
intención detectada
agente seleccionado
motivo de selección del agente
datos usados
permisos aplicados
decisiones del sistema
respuesta generada
archivos cargados
aprobaciones
rechazos
correcciones
cambios de estado
resultado final
errores
```

La trazabilidad debe ser visible de forma resumida para el usuario involucrado y más completa para Administrador y Usuario IC, según permisos.

---

# 11. UX e interfaz

La referencia visual principal serán los templates HTML entregados.

También se pueden usar como referencia secundaria:

```txt
screencapture-m3-material-1.png
screencapture-m3-material-2.png
chatbot-1.png
chatbot-2.png
```

La estructura visual general será:

```txt
menú lateral izquierdo
contenido principal a la derecha
logo de Personal Stock en la parte superior del menú lateral
usuario activo arriba a la derecha
avatar/foto circular 1:1
desplegable de perfil
Home con saludo
carousel de atajos
prompt principal en la base
respuestas del bot
acciones sugeridas
```

El diseño debe ser moderno, simple, corporativo y responsive.

---

# 12. Home, saludo y usuario logueado

Home será el punto principal de entrada.

Debe contener:

```txt
saludo personalizado
carousel de atajos
prompt principal
respuestas del bot
acciones sugeridas
conexión al orquestador n8n
```

El saludo debe usar el nombre de pila del usuario logueado.

Ejemplo:

```txt
Hola, Luciano
¿Cómo puedo ayudarte?
```

En el chatbot base existe actualmente:

```txt
js/config.js
```

con:

```js
CHAT_USER_ID = "benja"
```

Eso debe reemplazarse por una variable dinámica basada en el usuario logueado.

No debe quedar “Benja” como valor visible ni identificador fijo.

El mismo usuario logueado debe usarse para:

```txt
saludo
conversaciones
memoria
permisos
acciones
trazabilidad
feedback
correcciones
aprobaciones
```

---

# 13. Carousel de atajos

El carousel debe ubicarse entre el saludo superior y el prompt de la base, como en la referencia de los templates HTML entregados.

Debe incluir 8 accesos iniciales orientados a acciones del MVP y recursos del sitio, sin sugerir proactivamente búsquedas sobre antecedentes de mails enviados.

```txt
1. Generar un plan de comunicación
2. Crear copy para e-mail
3. Revisar tono y marca
4. Validar cumplimiento y riesgo
5. Pedir ideas creativas
6. Buscar templates y recursos
7. Ver roadmap y acciones
8. Consultar estado de una acción
```

Cada atajo debe disparar una intención clara para el orquestador.

Ejemplo:

```txt
Generar un plan de comunicación → generar_plan_comunicacion
Crear copy para e-mail → crear_copy_email
Revisar tono y marca → revisar_qa_editorial
Validar cumplimiento y riesgo → validar_cumplimiento
Pedir ideas creativas → pedir_ideas_creativas
Buscar templates y recursos → consultar_contenido_personalstock
Ver roadmap y acciones → consultar_roadmap
Consultar estado de una acción → consultar_acciones
```

Los atajos deben poder actualizarse luego desde backend o configuración.

---

# 14. Menú lateral

Estructura:

```txt
Home

Stock
  - Logos
  - Manuales de Marca

Templates
  - Presentaciones
  - E-mails
  - Viva Engage
  - Hojas membretadas

Mi firma
  - Firma para e-mails
  - Mi Data
  - Tarjetas personales en papel

Toolbox

Roadmap
```

En MVP 1, los contenidos pueden estar simulados, pero deben quedar rutas, navegación, layout, placeholders, estados vacíos y preparación para integrar contenido real.

Comportamiento del menú lateral:

```txt
solo un menú principal puede estar activo/desplegado a la vez
si un menú está desplegado y el usuario hace click en otro, el anterior debe colapsarse
el estado activo debe quedar visualmente claro
los submenús deben abrir/cerrar sin refrescar toda la app
```

---

# 15. Contenido heredado de Comustock

El sitemap del proyecto anterior Comustock está en:

```txt
comustock_base.csv
```

El contenido del proyecto anterior Comustock está en:

```txt
comustock-base
```

Ese contenido deberá alimentar o poblar secciones como:

```txt
Stock
Logos
Manuales de Marca
Templates
Presentaciones
E-mails
Viva Engage
Hojas membretadas
Mi firma
Firma para e-mails
Mi Data
Tarjetas personales en papel
Toolbox
Roadmap
```

Comustock no debe aparecer como nombre del producto final ni como marca del nuevo producto. Solo debe figurar cuando se haga referencia al proyecto anterior, sus carpetas, archivos, sitemap o contenido heredado.

---

# 16. Usuarios, perfiles y permisos

Crear una base demo de 100 usuarios.

Dentro de esos 100 usuarios deben incluirse los usuarios de prueba:

```txt
Luciano Zurlo - Administrador - Rol: Diseñador; Desarrollador - comustock.ci@gmail.com
Diego Ferrari - Usuario IC - Rol: Redactor - comustock.uci1@gmail.com
Sara Astudillo - Usuario IC - Rol: Diseñador/a - comustock.uci2@gmail.com
Martín Caso - Usuario IC - Rol: Productor - comustock.uci3@gmail.com
Sebastián Álvarez Hincaipié - Usuario IC - Rol: Productor - comustock.uci4@gmail.com
Emiliano Zabuski - Usuario IC - Rol: Redactor - comustock.uci5@gmail.com
Jonathan Ferraro - Usuario IC - Rol: Gerente Cultura - comustock.g2@gmail.com
Luciana Dau - Usuario IC - Rol: Gerente IC - comustock.g1@gmail.com
Pablo Giglio - Usuario - comustock.u1@gmail.com
Javier Vulich - Usuario - comustock.u2@gmail.com
Sebastián Marzico - Usuario - comustock.u3@gmail.com
Santiago Gugger - Usuario - comustock.u4@gmail.com
```

Perfiles:

```txt
Administrador
Usuario IC
Heavy user
Macro
Usuario
```

Roles para Usuario IC:

```txt
Diseñador
Desarrollador
Redactor
Productor
Gerente Cultura
Gerente IC
Especialista
```

La base demo debe permitir probar:

```txt
segmentación
audiencias
usuarios finales
usuarios IC
perfil Macro
Heavy user
aprobadores
usuarios Focus
usuarios sin permisos para contenido restringido
```

---

# 17. Restricciones de acceso al dataset

Si el campo `destinatario` del dataset contiene:

```txt
macro
macroestructura
líderes
lideres
```

el perfil `Usuario` no puede acceder a ese contenido.

El bot no debe mostrar, resumir, citar ni usar como contexto visible para usuarios finales las comunicaciones cuyo destinatario corresponda a esos grupos restringidos.

Respuesta segura sugerida:

```txt
Encontré información relacionada con ese tema, pero pertenece a comunicaciones restringidas para otro perfil de usuario. No tengo permiso para mostrar ese contenido.
```

El RAG debe filtrar por permisos antes de construir la respuesta final.

---

# 18. Backend y modelos

Stack propuesto:

```txt
Python
Django
Frontend responsive basado en templates HTML
n8n
Gemini inicialmente
```

Este stack es el propuesto como base. Si Kiro identifica un stack mejor o una incorporación técnica que mejore eficiencia, mantenibilidad, integración con n8n, rendimiento local o evolución futura, deberá considerarlo y justificarlo antes de implementarlo.

Modelos o entidades sugeridas:

```txt
Usuario
Perfil
Rol
Focus
Área
Proyecto
Aprobador
Brief
Comunicación
Archivo
WorkflowRun
AgentRun
ApprovalStep
MetricEvent
DatasetCommunication
DatasetLink
DatasetAttachment
ChatConversation
ChatMessage
UserMemory
ProjectMemory
MemoryConsent
ConversationSummary
AgentFeedback
CorrectionRecord
```

Los usuarios se cargarán desde CSV o semilla inicial.

Campos sugeridos para usuarios:

```txt
nombre
apellido
email
perfil
roles
cargo
es_focus
areas_focus
es_aprobador_default
puede_aprobar
avatar_url
memoria_habilitada
```

---

# 19. Dataset histórico de mails

El dataset histórico está en:

```txt
mails
```

Estructura disponible:

```txt
mails/attachments
mails/images
mails/output/contenido_md
mails/output/lotes
mails/output/relevamiento_enriquecido.json
mails/output/relevamiento_final.json
mails/output/relevamiento.csv
mails/output/relevamiento.json
mails/workflows n8n
mails/enriquecer.py
mails/unificar.py
```

Fuente principal para el agente RAG:

```txt
mails/output/relevamiento_enriquecido.json
```

Fuente de verdad de estructura:

```txt
ESTRUCTURA_DATASET.md
```

No se debe duplicar ni tratar como pendiente el viejo punto “campos nuevos del dataset”. Esos campos ya están incorporados en la estructura actual.

---

# 20. Agente de historial de mails / RAG

Este agente responde sobre el historial de mails internos.

Debe consultar:

```txt
mails/output/relevamiento_enriquecido.json
mails/output/contenido_md
mails/images
mails/attachments
```

Debe responder sobre:

```txt
comunicaciones históricas
mails enviados
campañas
tandas
comunicaciones segmentadas
audiencias
tono
estilo
categorías
links
adjuntos
imágenes
alcance
CCO
fechas
versiones
```

Flujo obligatorio:

```txt
1. Identificar usuario y perfil.
2. Interpretar consulta.
3. Buscar coincidencias.
4. Filtrar por permisos y destinatario.
5. Descartar contenido no permitido.
6. Priorizar comunicaciones recientes.
7. Diferenciar comunicación segmentada de tanda.
8. Revisar links, adjuntos e imágenes.
9. Advertir si la información puede estar desactualizada.
10. Responder con síntesis clara.
```

Reglas:

```txt
fecha_envio define vigencia
la comunicación más reciente prevalece
si la información es vieja, aclarar
si hay versiones contradictorias, priorizar la más reciente
no mezclar versiones viejas y nuevas
si sin_informacion = true, no tratar como contenido completo
si link es restringido_requiere_credenciales, avisar que requiere acceso interno
si existe *_UNIDA.png, tratarla como imagen principal
nombres_partes queda como trazabilidad
```

Regla de vigencia:

```txt
0 a 6 meses: probablemente vigente
6 a 18 meses: utilizable con aclaración de fecha
más de 18 meses: posiblemente desactualizada
sin fecha: baja confianza
```

---

# 21. Manual de Voz y Tono

El archivo:

```txt
brand_key_voz_tono_personal.md
```

debe usarse para:

```txt
Agente Redactor CI
QA Editorial
revisión de tono
generación de copies
validación de estilo Personal
```

Directivas de QA Editorial y Cumplimiento y Riesgo, si no están documentadas por separado, deberán cargarse como parámetros configurables en backend.

---

# 22. Trigger Comunicaciones

Trigger Comunicaciones es el agente que gestiona el proceso completo de una necesidad de comunicación. No debe ser solo un generador de texto.

Debe crear o actualizar un proyecto de comunicación con:

```txt
id del proyecto
solicitante
tipo de solicitante
brief
audiencia
canal
fecha tentativa
estado
Focus asignado
aprobadores
asistentes
documentos
copy
piezas
historial de cambios
aprobaciones
rechazos
comentarios
```

En MVP 1 solo estará disponible para comunicaciones por e-mail.

Canales futuros:

```txt
E-mail
Posteo en Viva Engage
WhatsApp
Cartelera
Producción en estudio dos x dos
```

Workflow:

```txt
1. Carga de solicitud / brief.
2. Optimización del brief.
3. Preguntas para completar datos faltantes.
4. Sugerencia de canal.
5. Carga de documentos de apoyo.
6. Oferta de tormenta de ideas.
7. Caso especial para usuario final y comunicación no masiva.
8. Asignación de Focus.
9. Identificación de aprobadores y asistentes.
10. Notificación al Gerente CI.
11. Posible desaprobación con justificación obligatoria.
12. Generación del plan de comunicación.
13. Generación o revisión del copy.
14. Redactor CI.
15. QA Editorial.
16. Cumplimiento y Riesgo.
17. Ajustes hasta pasar QA y cumplimiento.
18. Revisión del Focus.
19. Aprobación del requirente.
20. Aprobación de aprobadores.
21. Diseño de comunicación.
22. Carga de piezas diseñadas.
23. Validación de pieza.
24. Segmentación y alcance.
25. Calendarización.
26. Definición de envío manual o automatizado.
```

Datos mínimos para avanzar a plan:

```txt
qué se comunica
por qué se comunica
audiencia
fecha o ventana tentativa
canal
solicitante
nivel de urgencia
documentos de apoyo si existen
```

Si faltan datos críticos, debe devolver preguntas y no avanzar.

Comunicación full compañía:

```txt
Para: Comunicación Interna
CCO: cinterna@outlook.com
```

En MVP 1, la segmentación usará la base demo de 100 usuarios.

---

# 23. Agente Generador de propuestas creativas

Este agente explora enfoques, ideas, conceptos y alternativas de campaña.

Entrada:

```txt
brief
objetivo
audiencia
tono
canal
restricciones
referencias históricas si existen
```

Salida:

```txt
3 a 5 enfoques creativos
racional breve
posible asunto o título
idea de bajada
recomendación de canal
riesgos o cuidados
```

No reemplaza al Redactor CI ni al Trigger Comunicaciones.

---

# 24. Agente Redactor CI

Genera borradores de copy.

Entrada:

```txt
brief validado
audiencia
canal
tono
objetivo
historial relacionado
manual de voz y tono
restricciones
memoria del usuario si está habilitada
```

Salida:

```txt
asunto sugerido
preheader si corresponde
copy principal
CTA
versión alternativa si corresponde
notas de criterio editorial
supuestos usados
```

Para MVP 1, la salida principal será e-mail.

---

# 25. Agente QA Editorial

Revisa desde el punto de vista editorial, marca y claridad.

Debe revisar:

```txt
ortografía
gramática
claridad
tono
coherencia
consistencia con marca
adecuación a audiencia
longitud
CTA
asunto
preheader
```

Salida:

```txt
estado: aprobado | requiere_ajustes
observaciones
errores detectados
sugerencias
versión corregida si corresponde
nivel de confianza
```

No debe modificar silenciosamente el texto sin explicar qué cambió.

---

# 26. Agente Cumplimiento y Riesgo

Es gate obligatorio.

Debe detectar:

```txt
PII
datos sensibles
riesgo legal
riesgo reputacional
promesas o afirmaciones no validadas
información confidencial
audiencias incorrectas
links o adjuntos sensibles
temas que requieran revisión humana
```

Salida:

```txt
estado: aprobado | bloqueado | requiere_revision_humana | requiere_ajustes
riesgos_detectados
tipo de riesgo
severidad
recomendación
texto o sección afectada
acción sugerida
```

Si detecta riesgo alto, debe bloquear avance.

---

# 27. Roadmap Eventos

Roadmap Eventos es una vista general de acciones calendarizadas o por calendarizar.

Debe recibir eventos desde:

```txt
Trigger Comunicaciones
acciones generadas por agentes
eventos cargados manualmente
futuras integraciones de calendario
```

Cada entrada debe tener:

```txt
título
tipo
fecha
hora
estado
responsable
canal
proyecto asociado
dependencias
próxima acción
```

---

# 28. Aprobaciones y versionado

Cada aprobación debe registrarse como entidad.

Guardar:

```txt
proyecto
etapa
aprobador
rol del aprobador
estado
fecha de envío
fecha de respuesta
comentarios
versión evaluada
motivo de rechazo
```

Estados:

```txt
pendiente
aprobado
rechazado
requiere_ajustes
observador
omitido
```

Orden base:

```txt
Focus
↓
Requirente
↓
Aprobador o aprobadores
```

Todo contenido generado debe versionarse:

```txt
brief
plan de comunicación
copy
asunto
preheader
CTA
QA
cumplimiento
piezas
comentarios
```

No se debe sobrescribir una versión aprobada sin dejar historial.

---

# 29. Archivos y documentos

Cada archivo cargado debe guardar:

```txt
nombre original
tipo
tamaño
usuario que lo subió
fecha
proyecto asociado
etapa del workflow
uso previsto
ubicación
estado de procesamiento
resumen si fue procesado
```

Diferenciar:

```txt
archivo usado como contexto
archivo usado como adjunto final
archivo usado como pieza diseñada
```

En MVP 1, si Drive no queda integrado completamente, puede simularse o usarse almacenamiento local con contrato claro para migrar.

Drive mencionado:

```txt
comustock.ci@gmail.com
```

No incluir credenciales reales.

---

# 30. Memoria

La memoria debe estar asociada al usuario logueado.

Debe tener consentimiento inicial:

```txt
Activar memoria
No activar memoria
```

La memoria no debe guardar conversaciones literales como memoria permanente. Debe guardar resúmenes estructurados.

Desde perfil, el usuario debe poder:

```txt
activar memoria
desactivar memoria
ver estado
solicitar limpieza
```

También debe existir memoria por proyecto:

```txt
brief
decisiones
versiones
aprobaciones
estado
usuarios involucrados
```

---

# 31. Feedback y aprendizaje

Registrar correcciones:

```txt
usuario
fecha
agente
prompt original
respuesta original
corrección
motivo
versión corregida
tipo de error
```

Tipos de error:

```txt
tono incorrecto
copy largo
copy informal
copy frío
información incorrecta
no respetó marca
no respetó audiencia
riesgo legal
PII
canal mal sugerido
brief incompleto
estructura incorrecta
```

No asumir que el LLM aprende solo en tiempo real.

Implementar aprendizaje mediante:

```txt
memoria
feedback estructurado
correcciones
ajustes de prompts
mejora del RAG
reglas editoriales configurables
eventual fine-tuning posterior
```

---

# 32. Tablero y página de acciones

Tablero de métricas:

```txt
uso por agente
acciones corriendo
acciones finalizadas
comunicaciones generadas
briefs cargados
aprobaciones pendientes
aprobaciones rechazadas
correcciones recibidas
errores frecuentes
canales sugeridos
canales usados
usuarios activos
temas consultados
categorías frecuentes
```

Métricas del dataset:

```txt
comunicaciones segmentadas
mails agrupados
destinatarios totales
CCO total
imágenes unidas
sorteos
encuestas
fallecimientos
ganadores
entradas a eventos
tandas
```

Página de acciones:

```txt
acción
agente
usuario
estado
inicio
fin
próximo paso
responsable
resultado
error
```

Kiro deberá analizar si parte de las métricas de uso pueden obtenerse o complementarse mediante Google Analytics 4, usando un eslabón/nodo de GA4 en n8n o una integración equivalente. Esto no debe reemplazar la trazabilidad interna de agentes y workflows, pero puede complementar métricas de navegación, uso de páginas, eventos de interacción, clicks en atajos, uso del prompt y recorridos del usuario.

---

# 33. Integraciones externas

Posibles integraciones:

```txt
Google Drive
n8n
Gemini
Viva Engage
WhatsApp
E-mail
Calendarios
APIs de usuario / directorio interno
APIs de dotación futura
```

Para MVP 1, si alguna API no está disponible, debe quedar simulada o preparada con contrato.

Variables esperadas:

```txt
GEMINI_API_KEY
N8N_WEBHOOK_URL
DJANGO_SECRET_KEY
DATABASE_URL
GOOGLE_DRIVE_FOLDER_ID
```

No incluir claves reales.

---

# 34. Límites del MVP 1

MVP 1:

```txt
corre localmente
no se asume listo para 20.000 usuarios
Trigger Comunicaciones solo automatiza e-mail
Viva Engage, WhatsApp, Cartelera y Producción quedan preparados pero no automatizados
generación visual automática queda para MVP 2
variantes multicanal automáticas quedan para MVP 3
publicación orquestada multicanal queda para MVP 4
si una API externa no está disponible, se simula o se deja contrato
no se envían comunicaciones reales sin confirmación humana explícita
no se usan credenciales reales en el repo
```

---

# 35. Escalabilidad futura

La app está pensada para escalar hasta:

```txt
20.000 usuarios
```

Antes de escalar habrá que revisar:

```txt
autenticación robusta
permisos por perfil
control de acceso al dataset
base de datos productiva
índices de búsqueda
vector database escalable
caché
colas
procesamiento asíncrono
rate limits
observabilidad
logs
monitoreo
trazabilidad
backups
seguridad
sesiones
escalado horizontal
separación frontend/backend
despliegue cloud
almacenamiento externo
protección de datos
testing de carga
testing de permisos
testing de seguridad
costos de LLM
```

Kiro debe indicar qué partes del MVP local no están preparadas para esa escala.

---

# 36. Criterios de aceptación del MVP 1

El MVP 1 será aceptable si permite:

```txt
loguearse con usuarios demo
ver Home basada en los templates HTML entregados
mostrar saludo con usuario logueado
mostrar carousel de 8 atajos
usar prompt conectado al orquestador
derivar a agentes base según intención
consultar historial de mails con permisos y vigencia
bloquear contenido restringido para perfil Usuario
iniciar Trigger Comunicaciones
crear o simular proyecto de comunicación
generar o simular copy
pasar o simular QA Editorial
pasar o simular Cumplimiento y Riesgo
registrar estados y trazabilidad
ver acciones corriendo y finalizadas
ver tablero básico
cargar o simular documentos
usar base demo de 100 usuarios
documentar instalación local
documentar límites y próximos MVPs
```

---

# 37. Reglas para evitar errores

El sistema debe evitar:

```txt
inventar información del dataset
mostrar contenido restringido a usuarios sin permiso
mezclar versiones viejas y nuevas sin aclaración
presentar links restringidos como accesibles
tratar registros sin información como válidos
aprobar contenido sin QA y cumplimiento
enviar o simular envío real sin confirmación
perder trazabilidad de aprobaciones
sobrescribir versiones sin historial
usar Benja como usuario real
usar Comustock como nombre del producto final
crear agentes futuros como obligatorios del MVP 1
asumir que el MVP local soporta 20.000 usuarios
```

Si el sistema no sabe, no puede, no tiene permisos o no tiene información suficiente, debe decirlo claramente.

---

---

# 38. Instrucciones finales para Kiro

Kiro debe:

```txt
usar Personal Stock como nombre del producto
inspeccionar cs-chat-rag primero
usar templates/home.html y templates/login.html como base visual y estructural
usar templates/personal-stock-logo.svg y templates/personal-stock-logo-light.svg
usar comustock_base.csv y comustock-base como contenido heredado
usar mails/output/relevamiento_enriquecido.json para RAG
usar ESTRUCTURA_DATASET.md como fuente de verdad del dataset
usar brand_key_voz_tono_personal.md como manual de voz y tono
crear base demo de 100 usuarios
incluir usuarios de prueba
crear orquestador principal que coordine agentes
crear agentes obligatorios del MVP 1
documentar JSONs, webhooks, contratos y workflows n8n
generar spec plan, requisitos, diseño e implementación tarea por tarea
documentar limitaciones
documentar próximos MVPs
```


