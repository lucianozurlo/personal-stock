# Dataset de Comunicaciones Internas — Estructura y diccionario de datos

Este dataset es un relevamiento de ~5.300 comunicaciones internas históricas (newsletters
corporativos) de Personal/Telecom/Flow. Fue generado procesando los `.eml` originales con OCR
(el texto vive dentro de imágenes/flyers), y luego post-procesado en tres pasos: unión de
imágenes fragmentadas, agrupación de comunicaciones segmentadas, y enriquecimiento de links y
adjuntos.

Cada registro = una comunicación interna. Las comunicaciones que se enviaron partidas en varios
mails (mismo asunto + mismo día) se concentran en un único registro representativo.

El dataset final (con todo aplicado) es `relevamiento_enriquecido.json`.

---

## Pipeline de generación

1. **Loteo + OCR** → procesa los .eml, transcribe el texto de las imágenes con Gemini, detecta
   tipo de comunicación, cuenta destinatarios en CCO. Salida por lotes.
2. **Consolidar** → junta los lotes en `relevamiento.json` (+ xlsx/csv) y calcula tandas.
3. **Unificar** (`unificar.py`) → une imágenes fragmentadas de cada mail, agrupa comunicaciones
   segmentadas, suma cuentas CCO de los grupos. Salida: `relevamiento_final.json`.
4. **Enriquecer** (`enriquecer.py`) → chequea links y extrae contenido de links públicos y
   adjuntos a markdown + resumen. Salida final: `relevamiento_enriquecido.json`.

---

## Ejemplo completo de un registro

```json
{
  "id_mail": "Pedido de librería | ¡Tenemos novedades!",
  "fecha_envio": "2026-03-12",
  "asunto": "Pedido de librería | ¡Tenemos novedades!",
  "proyecto": "",
  "destinatario": "FULL COMPAÑÍA",
  "copy_completo": "NOVEDADES EN TUS PEDIDOS DE LIBRERÍA\n\nPara mejorar la experiencia, los pedidos de librería ahora se gestionan de forma centralizada en determinados edificios y se realizan directamente desde iTicket.\n\nA la hora de hacer tu solicitud, tené en cuenta:\n- Para envíos al interior del país, el monto mínimo es de USD 200.\n- Las entregas se realizan en domicilios habilitados (podés verlos en el adjunto).\n\nMejor experiencia, en menos pasos.",
  "resumen": "Los pedidos de librería ahora se gestionan de forma centralizada desde iTicket. Monto mínimo de USD 200 para envíos al interior y entregas en domicilios habilitados.",

  "entradas_evento": false,
  "evento_detalle": "",
  "es_fallecimiento": false,
  "es_encuesta": false,
  "es_sorteo": false,
  "es_ganadores": false,
  "sin_informacion": false,

  "cuentas_cco": 1240,
  "cuentas_cco_total": 3680,
  "destinatarios_total": 3685,
  "mails_en_grupo": 3,
  "ids_del_grupo": "Pedido de librería (parte 1) | Pedido de librería (parte 2) | Pedido de librería (parte 3)",

  "imagenes_descargadas": 2,
  "nombres_imagenes": "00342_Pedido_de_libreria_01_image001_UNIDA.png",
  "nombres_partes": "00342_Pedido_de_libreria_01_image001.png | 00342_Pedido_de_libreria_02_image002.png",

  "links_detectados": "https://forms.office.com/r/abc123 | https://goo.gl/maps/xyz",
  "cantidad_links": 2,
  "tiene_adjuntos": true,
  "nombres_adjuntos": "Domicilios-habilitados.pdf",
  "posible_tanda": false,
  "grupo_tanda": "T087",
  "estilo_diseno": "corporativo, infografía",
  "tono_mensaje": "institucional",
  "categoria_probable": "Beneficios",
  "observaciones": "con adjuntos",

  "links_accesibles": 1,
  "links_restringidos": 1,
  "links_rotos": 0,
  "links_detalle": [
    { "url": "https://forms.office.com/r/abc123", "status": null, "clase": "restringido_requiere_credenciales", "md_file": "", "resumen": "" },
    { "url": "https://goo.gl/maps/xyz", "status": 200, "clase": "accesible", "md_file": "link_a1b2c3d4e5f6.md", "resumen": "Ubicación del depósito central — Av. Corrientes 1234, CABA. Horario de retiro de 9 a 18hs." }
  ],
  "links_contenido_md": "link_a1b2c3d4e5f6.md",
  "links_resumen": "https://goo.gl/maps/xyz: Ubicación del depósito central — Av. Corrientes 1234, CABA...",

  "adjuntos_detalle": [
    { "nombre": "Domicilios-habilitados.pdf", "md_file": "adj_Domicilios-habilitados_9f8e7d6c.md", "resumen": "Listado de domicilios habilitados para entregas: Edificio Central (CABA), Sede Norte (Vicente López), Sede Sur (Avellaneda)." }
  ],
  "adjuntos_contenido_md": "adj_Domicilios-habilitados_9f8e7d6c.md",
  "adjuntos_resumen": "Domicilios-habilitados.pdf: Listado de domicilios habilitados para entregas: Edificio Central (CABA)..."
}
```

---

## Diccionario de campos

### Datos base de la comunicación

| Campo | Tipo | Qué trae |
|---|---|---|
| `id_mail` | texto | Identificador legible (deriva del nombre del .eml; suele ser el asunto). |
| `fecha_envio` | texto `YYYY-MM-DD` | Fecha de envío. Vacío si el .eml no la tenía. |
| `asunto` | texto | Asunto del mail. |
| `proyecto` | texto | Proyecto/campaña central si existe (SIT26, EM25, Colonia de Vacaciones...). Vacío si no hay uno claro. |
| `destinatario` | texto | A quién va dirigido (lo que sigue a "PARA:" en el cuerpo). `no_detectado` si no se encontró. |
| `copy_completo` | texto | Texto completo de la comunicación, transcripto por OCR desde las imágenes/flyer. Con saltos de línea. Sin el logo de marca del encabezado. Si no hay nada que extraer, dice `"Sin información"`. |
| `resumen` | texto | 1-2 frases directas con el mensaje central. |
| `estilo_diseno` | texto | Estilo visual (corporativo, infografía, colorido ilustrado, fotográfico...). |
| `tono_mensaje` | texto | Tono (institucional, festivo, motivacional, urgente...). |
| `categoria_probable` | texto | Categoría temática (Beneficios, RRHH, IT/Seguridad, Eventos, Formación, Colonia de Vacaciones, Salud, Reconocimiento, Tecnología, General). |
| `observaciones` | texto | Notas automáticas (con adjuntos, destinatario no detectado, pertenencia a tanda, errores de OCR). |

### Marcadores de tipo de comunicación (booleanos)

Detectan tipos específicos de comunicación. Se determinan combinando el modelo de OCR (Gemini lo
identifica al leer el flyer) con un respaldo por palabras clave sobre el texto. Un mismo registro
puede tener varios en `true`.

| Campo | Tipo | Qué marca |
|---|---|---|
| `entradas_evento` | booleano | Regala/sortea/invita a ganar **entradas, tickets o invitaciones** para un evento (recital, cine, teatro, partido, festival, show). |
| `evento_detalle` | texto | Si `entradas_evento` es true: nombre del evento/artista y tipo (ej: "Recital de Coldplay"). Vacío si no aplica. |
| `es_fallecimiento` | booleano | Informa el **fallecimiento** de una persona (obituario, condolencias, q.e.p.d.). |
| `es_encuesta` | booleano | Invita a responder una **encuesta**, sondeo o cuestionario. |
| `es_sorteo` | booleano | Anuncia un **sorteo** o invita a participar para ganar algo (premios, regalos; no necesariamente entradas). |
| `es_ganadores` | booleano | Comunica **quiénes ganaron** o resultaron ganadores de algo. |
| `sin_informacion` | booleano | `true` cuando el registro **no tiene contenido útil**: sin copy, sin imágenes y sin adjuntos. En esos casos `copy_completo` dice "Sin información". |

### Destinatarios (cuentas CCO)

Las comunicaciones masivas envían a muchas cuentas de usuarios en CCO (BCC). Estos campos cuentan
esas cuentas.

| Campo | Tipo | Qué trae |
|---|---|---|
| `cuentas_cco` | número | Cantidad de cuentas en CCO de **este** mail individual. |
| `cuentas_cco_total` | número | Cantidad de cuentas en CCO **sumando todos los mails del grupo** (ver "comunicación segmentada"). Si no es grupo, igual a `cuentas_cco`. |
| `destinatarios_total` | número | Cuentas en CCO + To + CC (sumadas en el grupo si aplica). Es el total de destinatarios alcanzados. |

### Comunicación segmentada (agrupación de mails)

Cuando una misma comunicación se envía partida en varios mails (porque va a miles de cuentas, se
manda por tandas), esos mails tienen el **mismo asunto exacto y el mismo día**. El dataset los
concentra en **un único registro representativo** (el de copy más completo).

| Campo | Tipo | Qué trae |
|---|---|---|
| `mails_en_grupo` | número | Cuántos mails formaban esta comunicación. `1` si fue un mail único. |
| `ids_del_grupo` | texto | Los `id_mail` de todos los mails del grupo (separados por ` \| `). Vacío si no es grupo. Sirve de trazabilidad. |

### Imágenes (y unión de fragmentos)

Cuando el flyer del cuerpo está cortado en varias imágenes (image001, image002...), se unen
verticalmente (una debajo de otra, ordenadas por nombre) en una sola imagen "completa". Las
imágenes originales se conservan en disco.

| Campo | Tipo | Qué trae |
|---|---|---|
| `imagenes_descargadas` | número | Cantidad de imágenes que tenía el mail en el cuerpo. |
| `nombres_imagenes` | texto | Si se unieron: el nombre de la **imagen unida** (`*_UNIDA.png`). Si era una sola: su nombre. |
| `nombres_partes` | texto | Si se unieron: los nombres de las **imágenes originales** que forman la unida (separados por ` \| `, en orden). Vacío si no hubo unión. |

Las imágenes unidas se guardan en `images/*_UNIDA.png`; las originales siguen en `images/`.

### Tandas (campañas relacionadas)

Distinto de "comunicación segmentada": las tandas agrupan comunicaciones **relacionadas pero
distintas** (una campaña con varias piezas), no copias del mismo mail.

| Campo | Tipo | Qué trae |
|---|---|---|
| `posible_tanda` | booleano | `true` si forma parte de una serie/campaña de comunicaciones relacionadas. |
| `grupo_tanda` | texto | ID del grupo/tanda (T001, T002...). Las ediciones anuales (SIT25 vs SIT26) quedan separadas. |

### Links

| Campo | Tipo | Qué trae |
|---|---|---|
| `links_detectados` | texto | Todos los links del mail (separados por ` \| `). |
| `cantidad_links` | número | Cuántos links se detectaron. |
| `links_accesibles` | número | Links públicos que respondieron OK. |
| `links_restringidos` | número | Links que requieren login/credenciales corporativas. |
| `links_rotos` | número | Links con 404, error o sin respuesta. |
| `links_detalle` | lista | Un objeto por link: `url`, `status` (HTTP), `clase`, `md_file`, `resumen`. |
| `links_contenido_md` | texto | Nombres de los .md extraídos de links accesibles. |
| `links_resumen` | texto | Resúmenes concatenados de los links accesibles. |

**Valores de `clase` (por link):**
- `accesible` — respondió 200, es público → se extrajo el contenido a markdown.
- `restringido_requiere_credenciales` — pide login/SSO o devolvió 401/403 (SharePoint, SuccessFactors, Yammer, Forms, Webex, etc.).
- `roto_404` — no existe.
- `sin_respuesta_timeout` — no respondió en 15s.
- `error_XXX` — otro código de error HTTP.
- `ruido_tecnico` — namespace XML o fuente (w3.org, schemas.microsoft, googleapis) → no es un link real, se descarta.

### Adjuntos

| Campo | Tipo | Qué trae |
|---|---|---|
| `tiene_adjuntos` | booleano | Si el mail tenía adjuntos. |
| `nombres_adjuntos` | texto | Nombres originales de los adjuntos (separados por ` \| `). |
| `adjuntos_detalle` | lista | Un objeto por adjunto: `nombre`, `md_file`, `resumen`. |
| `adjuntos_contenido_md` | texto | Nombres de los .md con el contenido extraído. |
| `adjuntos_resumen` | texto | Resúmenes concatenados de los adjuntos. |

**Extracción de adjuntos:** se extrae texto de PDF, DOCX, XLSX y PPTX → markdown + resumen.
Adjuntos escaneados, `.rpmsg` (cifrados) o `.zip` se marcan como "sin texto extraíble".

---

## Archivos del contenido completo

Además del JSON, en `output/contenido_md/` hay un markdown por cada link accesible y cada adjunto
con texto:
- `link_<hash>.md` — contenido completo de un link público.
- `adj_<nombre>_<hash>.md` — contenido completo de un adjunto.

El JSON trae el **resumen**; el `.md` correspondiente trae el **texto completo**.
Las imágenes (originales y unidas) están en `images/`.

---

## Notas importantes para usar el dataset

1. **Comunicaciones segmentadas concentradas**: si una comunicación se envió en varios mails
   (mismo asunto + mismo día), aparece como **un solo registro**. `mails_en_grupo` dice cuántos
   eran y `ids_del_grupo` los lista. Las cuentas CCO de todos esos mails se suman en
   `cuentas_cco_total`.

2. **Imágenes unidas**: cuando un flyer venía partido en varias imágenes, `nombres_imagenes` tiene
   la imagen unida (`*_UNIDA.png`) y `nombres_partes` las originales. Las imágenes se apilan
   verticalmente, centradas por ancho.

3. **Registros sin contenido**: cuando un mail no tiene copy ni imágenes ni adjuntos (imágenes de
   origen corruptas), `sin_informacion` es `true` y `copy_completo` dice "Sin información".

4. **El relevamiento de links se hizo desde una máquina sin acceso a la red interna**, así que la
   mayoría de los links internos figuran como `restringido_requiere_credenciales`. Es correcto e
   informativo: el recurso existe pero requiere acceso interno. Solo los links públicos tienen
   contenido extraído.

5. **Tres niveles de información por comunicación**, útil para un chatbot:
   - `copy_completo` → el texto del flyer/comunicación.
   - `resumen`, `links_resumen`, `adjuntos_resumen` → versión corta para respuestas rápidas.
   - Los archivos `.md` en `contenido_md/` → texto completo de links y adjuntos.

6. **Los marcadores de tipo** (`entradas_evento`, `es_fallecimiento`, `es_encuesta`, `es_sorteo`,
   `es_ganadores`) permiten al chatbot filtrar o reconocer rápidamente el tipo de comunicación sin
   interpretar el copy. Son booleanos; un registro puede tener varios activos.

7. **Para citar o decidir si mostrar un recurso**, el campo `clase` de cada link indica si el
   contenido está disponible (`accesible`) o si hay que avisar que requiere acceso interno.
