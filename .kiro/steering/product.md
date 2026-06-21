---
inclusion: always
---

# Personal Stock

## Propósito

Personal Stock es una app web de apoyo a Comunicación Interna y Cultura de Personal.
En MVP 1 el foco está en:

- login
- home con prompt conversacional
- orquestador
- usuarios demo
- permisos por perfil
- trazabilidad
- RAG de mails históricos
- Trigger Comunicaciones para e-mail
- acciones y métricas básicas

## Reglas de naming

- El nombre visible del producto es siempre Personal Stock.
- "Comustock" es únicamente contenido heredado o material fuente, nunca marca vigente.
- No renombrar carpetas físicas heredadas si eso rompe rutas existentes.

## Fuente visual

- templates/login.html es la fuente principal de login.
- templates/home.html es la fuente principal de home.
- templates/img/personal-stock-logo.svg y templates/img/personal-stock-logo-light.svg son los logos oficiales.
- Los assets de los templates viven en subcarpetas: templates/css/ (estilos) y templates/js/ (scripts), referenciados desde login.html y home.html.
- No rediseñar desde cero los templates base. Integrar, no reinventar.

## Restricciones funcionales

- No exponer contenido restringido del dataset a perfiles no autorizados.
- No enviar comunicaciones reales sin confirmación humana explícita.
- No usar usuarios hardcodeados como "Benja".
- No simular que una acción fue realizada si no se ejecutó correctamente.
- Si el sistema no sabe, no puede, no tiene permisos o no tiene información suficiente, debe decirlo claramente.

## Alcance MVP 1

- Corre localmente. No se asume preparado para 20.000 usuarios.
- Trigger Comunicaciones solo automatiza e-mail.
- Viva Engage, WhatsApp, Cartelera y Producción quedan preparados pero no automatizados.
- Si una API externa no está disponible, se simula o se deja contrato documentado.
