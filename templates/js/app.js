const STORAGE_KEY = "comustock";

      const STARTER_PRESETS = {
        analizar: {
          label: "Analizar",
          items: [
            "Analizar este texto y resumirlo con los puntos clave.",
            "Analizar este contenido y detectar oportunidades de mejora.",
            "Analizar esta idea y señalar riesgos, ventajas y próximos pasos.",
            "Analizar este mensaje y reescribirlo más claro y profesional.",
          ],
        },
        escribir: {
          label: "Escribir",
          items: [
            "Escribir un mail claro y profesional a partir de esta idea.",
            "Escribir una propuesta breve, directa y convincente.",
            "Escribir preguntas frecuentes para este proyecto.",
            "Escribir un texto con tono simple, claro y humano.",
          ],
        },
        planificar: {
          label: "Planificar",
          items: [
            "Planificar este proyecto paso a paso con prioridades y tiempos.",
            "Planificar una estrategia simple para ejecutar esta idea.",
            "Planificar tareas concretas para avanzar sin perder tiempo.",
            "Planificar un roadmap corto con entregables claros.",
          ],
        },
      };

      if (!window.PS_USER || !window.PS_USER.firstName) {
        console.error(
          "PS_USER no está definido. El usuario debe estar autenticado.",
        );
        window.location.href = "/login/";
      }

      const RANDOM_GREETINGS = [
        `Hola ${window.PS_USER.firstName}!`,
        "__TIME_BASED__",
        `¿Todo bien, ${window.PS_USER.firstName}?`,
        `¿Cómo va, ${window.PS_USER.firstName}?`,
        `Ey, ${window.PS_USER.firstName}, ¿todo ok?`,
        `Che ${window.PS_USER.firstName}, ¿todo bien?`,
        `Buenas, ${window.PS_USER.firstName}!`,
        `¿Qué hacés, ${window.PS_USER.firstName}?`,
        `¿Cómo andás, ${window.PS_USER.firstName}?`,
        `${window.PS_USER.firstName}, ¿todo joya?`,
        `Hola, ${window.PS_USER.firstName}, ¿cómo va?`,
        `${window.PS_USER.firstName}, ¿cómo estás?`,
        `Buenas, ${window.PS_USER.firstName}, ¿va?`,
        `¿Todo tranqui, ${window.PS_USER.firstName}?`,
        `${window.PS_USER.firstName}, ¿qué contás?`,
        `Hola ${window.PS_USER.firstName}, ¿todo?`,
        `Ey ${window.PS_USER.firstName}, ¿cómo va?`,
        `Che, ${window.PS_USER.firstName}, ¿todo?`,
        `¿Qué onda, ${window.PS_USER.firstName}?`,
        `${window.PS_USER.firstName}, ¿en qué andás?`,
      ];

      const N8N_WEBHOOK_URL = "http://localhost:5678/webhook/comustock-chat";

// Estado global de la aplicación
      let typingTimeout = null;
      let attachMenuTimeout = null;
      let starterDropdownTimeout = null;
      let isAwaitingResponse = false;
      let isTransitioning = false;
      let isLockedUntilReplyFinishes = false;
      let activeStarterGroup = null;

// Referencias al DOM
      const app = document.getElementById("app");
      const introSlot = document.getElementById("introSlot");
      const welcomeTitle = document.getElementById("welcomeTitle");
      const dockSlot = document.getElementById("dockSlot");
      const messages = document.getElementById("messages");
      const template = document.getElementById("composerTemplate");
      const starterDropdown = document.getElementById("starterDropdown");
      const starterDropdownClose = document.getElementById("starterDropdownClose");
      const starterList = document.getElementById("starterList");
      const starterButtons = Array.from(document.querySelectorAll(".starter-chip"));

      // Instanciar composer desde template
      const composerShell = template.content.firstElementChild.cloneNode(true);
      introSlot.appendChild(composerShell);

      const composerForm = composerShell.querySelector("#composerForm");
      const composerInput = composerShell.querySelector("#composerInput");
      const sendBtn = composerShell.querySelector("#sendBtn");
      const clearBtn = composerShell.querySelector("#clearBtn");
      const attachBtn = composerShell.querySelector("#attachBtn");
      const attachMenu = composerShell.querySelector("#attachMenu");
      const attachItems = Array.from(composerShell.querySelectorAll("[data-attach]"));
      const composerHint = document.querySelector(".composer-hint");
      if (composerHint && composerHint.parentElement !== document.body) {
        document.body.appendChild(composerHint);
      }
      let composerHintFrame = null;


      const INTRO_PLACEHOLDER = "¿Cómo puedo ayudarte?";
      const CHAT_PLACEHOLDER = "Escribí acá...";
      let placeholderTypeTimeout = null;
      let placeholderFadeTimeout = null;

      function stopPlaceholderAnimation() {
        clearTimeout(placeholderTypeTimeout);
        clearTimeout(placeholderFadeTimeout);
        composerInput.classList.remove("placeholder-fading");
      }

      function setPlaceholderImmediate(text) {
        stopPlaceholderAnimation();
        composerInput.placeholder = text;
      }

      function typePlaceholder(text, options = {}) {
        const { delay = 0, speed = 42 } = options;
        stopPlaceholderAnimation();
        composerInput.placeholder = "";

        placeholderTypeTimeout = setTimeout(() => {
          let index = 0;
          const tick = () => {
            composerInput.placeholder = text.slice(0, index);
            if (index < text.length) {
              index += 1;
              placeholderTypeTimeout = setTimeout(tick, speed);
            }
          };
          tick();
        }, delay);
      }

      function fadeOutPlaceholder(options = {}) {
        const { duration = 240, after } = options;
        stopPlaceholderAnimation();
        composerInput.classList.add("placeholder-fading");
        placeholderFadeTimeout = setTimeout(() => {
          composerInput.placeholder = "";
          composerInput.classList.remove("placeholder-fading");
          if (typeof after === "function") after();
        }, duration);
      }


      function updateComposerHintPosition(rect) {
        if (!composerHint) return;
        const targetRect = rect || composerShell.getBoundingClientRect();
        if (!targetRect || !targetRect.width || !targetRect.height) return;
        composerHint.style.setProperty("--ps-hint-left", `${Math.round(targetRect.left)}px`);
        composerHint.style.setProperty("--ps-hint-top", `${Math.round(targetRect.bottom + 10)}px`);
        composerHint.style.setProperty("--ps-hint-width", `${Math.round(targetRect.width)}px`);
      }

      function scheduleComposerHintUpdate(rect) {
        if (!composerHint) return;
        cancelAnimationFrame(composerHintFrame);
        composerHintFrame = requestAnimationFrame(() => updateComposerHintPosition(rect));
      }

      function showComposerHint(options = {}) {
        if (!composerHint) return;
        const { immediate = false, rect = null } = options;
        updateComposerHintPosition(rect);
        composerHint.classList.remove("is-hidden", "is-closing-hidden");
        if (immediate) {
          composerHint.classList.add("is-visible");
          return;
        }
        requestAnimationFrame(() => composerHint.classList.add("is-visible"));
      }

      function hideComposerHint() {
        if (!composerHint) return;
        updateComposerHintPosition();
        composerHint.classList.remove("is-visible");
        composerHint.classList.add("is-hidden", "is-closing-hidden");
      }

      // ─── Helpers de estado de UI ───────────────────────────────────────────────

      function isChatting() {
        return app.classList.contains("is-chatting");
      }

      function getTimeBasedGreeting() {
        const hour = new Date().getHours();
        const name = window.PS_USER.firstName;
        if (hour >= 5 && hour < 12) return `¡Buen día, ${name}!`;
        if (hour >= 12 && hour < 20) return `¡Buenas tardes, ${name}!`;
        return `¡Buenas noches, ${name}!`;
      }

      function setRandomGreeting() {
        const greeting = RANDOM_GREETINGS[Math.floor(Math.random() * RANDOM_GREETINGS.length)];
        welcomeTitle.textContent = greeting === "__TIME_BASED__" ? getTimeBasedGreeting() : greeting;
      }

      function toggleSendState() {
        sendBtn.disabled =
          isLockedUntilReplyFinishes ||
          isAwaitingResponse ||
          isTransitioning ||
          !composerInput.value.trim();
      }

      // ─── Resize y métricas del dock ───────────────────────────────────────────

      function updateDockMetrics() {
        requestAnimationFrame(() => {
          const dockHeight =
            Math.ceil(document.getElementById("dock").getBoundingClientRect().height) || 180;
          app.style.setProperty("--dock-h", `${dockHeight}px`);
        });
      }

      function autoResize() {
        composerInput.style.height = "auto";
        composerInput.style.height = Math.min(composerInput.scrollHeight, 220) + "px";
        updateDockMetrics();
        scheduleComposerHintUpdate();
      }

      // ─── Mensajes ─────────────────────────────────────────────────────────────

      function scrollToBottom() {
        requestAnimationFrame(() => {
          const conv = document.querySelector(".conversation");
          conv.scrollTop = conv.scrollHeight;
        });
      }

      function createMessageRow(role, text, isTyping = false) {
        const row = document.createElement("div");
        row.className = `message-row ${role}${isTyping ? " typing" : ""}`;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";

        if (isTyping) {
          bubble.innerHTML = `
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    `;
        } else {
          bubble.textContent = text;
        }

        row.appendChild(bubble);
        return row;
      }

      function appendMessage(role, text, options = {}) {
        const row = createMessageRow(role, text, options.typing);
        messages.appendChild(row);
        scrollToBottom();
        return row;
      }

      // ─── Persistencia (deshabilitada) ─────────────────────────────────────────

      function getStoredMessages() {
        try {
          const raw = localStorage.getItem(STORAGE_KEY);
          const parsed = raw ? JSON.parse(raw) : [];
          return Array.isArray(parsed) ? parsed : [];
        } catch {
          return [];
        }
      }

      function saveMessages() {
        // localStorage deshabilitado temporalmente
      }

      function loadMessages() {
        const stored = getStoredMessages();
        if (!stored.length) {
          autoResize();
          toggleSendState();
          return;
        }

        stored.forEach((item) => {
          messages.appendChild(createMessageRow(item.role, item.text));
        });

        enterChatModeWithoutAnimation();
        scrollToBottom();
        autoResize();
        toggleSendState();
      }

// ─── Attach menu ──────────────────────────────────────────────────────────

      function openAttachMenu() {
        clearTimeout(attachMenuTimeout);
        attachMenu.hidden = false;
        requestAnimationFrame(() => attachMenu.classList.add("is-open"));
        attachBtn.classList.add("is-active");
      }

      function closeAttachMenu() {
        clearTimeout(attachMenuTimeout);
        attachMenu.classList.remove("is-open");
        attachBtn.classList.remove("is-active");
        attachMenuTimeout = setTimeout(() => {
          attachMenu.hidden = true;
        }, 220);
      }

      function toggleAttachMenu() {
        if (attachMenu.hidden || !attachMenu.classList.contains("is-open")) {
          openAttachMenu();
        } else {
          closeAttachMenu();
        }
      }

      // ─── Starter dropdown ─────────────────────────────────────────────────────

      function closeStarterDropdown() {
        clearTimeout(starterDropdownTimeout);
        starterDropdown.classList.remove("is-open");
        activeStarterGroup = null;
        starterButtons.forEach((button) => button.classList.remove("is-active"));
        starterDropdownTimeout = setTimeout(() => {
          starterDropdown.hidden = true;
        }, 220);
      }

      function openStarterDropdown(group) {
        const preset = STARTER_PRESETS[group];
        if (!preset) return;

        activeStarterGroup = group;
        starterButtons.forEach((button) => {
          button.classList.toggle("is-active", button.dataset.group === group);
        });

        starterList.innerHTML = "";

        preset.items.forEach((item) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "starter-item";
          button.textContent = item;
          button.addEventListener("click", () => {
            composerInput.value = item;
            autoResize();
            toggleSendState();
            closeStarterDropdown();
            composerInput.focus();
            composerInput.setSelectionRange(composerInput.value.length, composerInput.value.length);
          });
          starterList.appendChild(button);
        });

        clearTimeout(starterDropdownTimeout);
        starterDropdown.hidden = false;
        requestAnimationFrame(() => starterDropdown.classList.add("is-open"));
      }

      function toggleStarterDropdown(group) {
        if (activeStarterGroup === group && !starterDropdown.hidden) {
          closeStarterDropdown();
          return;
        }
        openStarterDropdown(group);
      }

      // ─── Animaciones de transición del composer ───────────────────────────────

      function measureComposerHeight(width, useChatLayout = false) {
        const clone = composerShell.cloneNode(true);
        clone.classList.remove("composer-floating");
        clone.classList.toggle("is-chat-layout", useChatLayout);
        clone.style.position = "fixed";
        clone.style.left = "-10000px";
        clone.style.top = "0";
        clone.style.width = `${width}px`;
        clone.style.height = "auto";
        clone.style.visibility = "hidden";
        clone.style.pointerEvents = "none";
        clone.style.transition = "none";

        const cloneInput = clone.querySelector("#composerInput");
        if (cloneInput) {
          cloneInput.value = composerInput.value;
          cloneInput.style.height = "auto";
          cloneInput.style.height = `${Math.min(cloneInput.scrollHeight || 0, useChatLayout ? 220 : 132)}px`;
        }

        document.body.appendChild(clone);
        const measured = Math.ceil(clone.getBoundingClientRect().height || 0);
        clone.remove();
        return measured || Math.ceil(composerShell.getBoundingClientRect().height || 0);
      }

      function computeDockRect() {
        const appRect = app.getBoundingClientRect();
        const slotRect = dockSlot.getBoundingClientRect();
        const appStyles = getComputedStyle(app);
        const slotStyles = getComputedStyle(dockSlot);
        const bottomOffset = parseFloat(appStyles.getPropertyValue("--composer-bottom-offset") || "0") || 0;
        const slotPaddingLeft = parseFloat(slotStyles.paddingLeft || "0") || 0;
        const slotPaddingRight = parseFloat(slotStyles.paddingRight || "0") || 0;
        const slotPaddingBottom = parseFloat(slotStyles.paddingBottom || "0") || 0;
        const slotWidth = slotRect.width || appRect.width;
        const availableWidth = Math.max(0, slotWidth - slotPaddingLeft - slotPaddingRight);
        const chatComposerWidth = parseFloat(appStyles.getPropertyValue("--chat-composer-w") || "860") || 860;
        const finalWidth = Math.min(chatComposerWidth, availableWidth);
        const finalHeight = measureComposerHeight(finalWidth, true);

        return {
          left: (slotRect.left || appRect.left) + slotPaddingLeft + Math.max(0, (availableWidth - finalWidth) / 2),
          top: appRect.bottom - finalHeight - bottomOffset - slotPaddingBottom,
          width: finalWidth,
          height: finalHeight,
        };
      }

      function computeIntroRect() {
        const slotRect = introSlot.getBoundingClientRect();
        const shellRect = composerShell.getBoundingClientRect();
        const finalWidth = slotRect.width || shellRect.width;
        const finalHeight = measureComposerHeight(finalWidth, false);
        return {
          left: slotRect.left + (slotRect.width - finalWidth) / 2,
          top: slotRect.top,
          width: finalWidth,
          height: finalHeight,
        };
      }

      function createIntroComposerGhost() {
        const oldGhost = introSlot.querySelector(".intro-return-ghost");
        if (oldGhost) oldGhost.remove();

        const ghost = composerShell.cloneNode(true);
        ghost.classList.remove("composer-floating", "is-chat-layout");
        ghost.classList.add("intro-return-ghost");
        ghost.style.position = "";
        ghost.style.left = "";
        ghost.style.top = "";
        ghost.style.width = "";
        ghost.style.height = "";
        ghost.style.visibility = "hidden";
        ghost.style.pointerEvents = "none";
        ghost.querySelectorAll(".has-text").forEach((el) => el.classList.remove("has-text"));

        const ghostClear = ghost.querySelector(".clear-icon");
        if (ghostClear) {
          ghostClear.style.opacity = "0";
          ghostClear.style.width = "0px";
          ghostClear.style.minWidth = "0px";
          ghostClear.style.flex = "0 0 0";
          ghostClear.style.flexBasis = "0px";
          ghostClear.style.padding = "0";
          ghostClear.style.margin = "0";
          ghostClear.style.overflow = "hidden";
          ghostClear.style.pointerEvents = "none";
        }

        ghost.setAttribute("aria-hidden", "true");
        ghost.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
        ghost.querySelectorAll("button, textarea, input, select, a").forEach((el) => {
          el.setAttribute("tabindex", "-1");
        });

        const ghostInput = ghost.querySelector("textarea");
        if (ghostInput) {
          ghostInput.value = "";
          ghostInput.placeholder = INTRO_PLACEHOLDER;
          ghostInput.removeAttribute("style");
          ghostInput.style.height = "";
        }

        introSlot.appendChild(ghost);
        return ghost;
      }

      function normalizeComposerForIntroLayout() {
        composerForm.classList.remove("has-text");
        composerInput.value = "";
        composerInput.style.height = "";
        composerInput.style.minHeight = "";
      }

      function getRectFromElement(el) {
        const rect = el.getBoundingClientRect();
        return {
          left: rect.left,
          top: rect.top,
          width: rect.width,
          height: rect.height,
        };
      }

      function clearComposerInlineMotion() {
        composerShell.style.position = "";
        composerShell.style.left = "";
        composerShell.style.top = "";
        composerShell.style.width = "";
        composerShell.style.height = "";
      }

      function enterChatModeWithoutAnimation() {
        document.getElementById("dock")?.classList.remove("dock-fading");
        composerShell.classList.add("is-chat-layout");
        dockSlot.appendChild(composerShell);
        app.classList.remove("is-transitioning");
        app.classList.add("is-chatting");
        setPlaceholderImmediate(CHAT_PLACEHOLDER);
        updateDockMetrics();
        requestAnimationFrame(() => showComposerHint({ immediate: true }));
        toggleSendState();
        closeStarterDropdown();
      }

      function transitionToChatMode() {
        if (isChatting() || isTransitioning) return Promise.resolve();

        isTransitioning = true;
        toggleSendState();
        closeStarterDropdown();
        closeAttachMenu();
        hideComposerHint();
        setPlaceholderImmediate("");

        const startRect = composerShell.getBoundingClientRect();
        introSlot.style.minHeight = `${Math.ceil(startRect.height)}px`;
        const endRect = computeDockRect();

        composerShell.classList.add("composer-floating");
        composerShell.style.left = `${startRect.left}px`;
        composerShell.style.top = `${startRect.top}px`;
        composerShell.style.width = `${startRect.width}px`;
        composerShell.style.height = `${startRect.height}px`;
        composerShell.style.position = "fixed";

        document.body.appendChild(composerShell);
        app.classList.add("is-transitioning");

        return new Promise((resolve) => {
          requestAnimationFrame(() => {
            composerShell.classList.add("is-chat-layout");
            typePlaceholder(CHAT_PLACEHOLDER, { delay: 160, speed: 42 });

            const animation = composerShell.animate(
              [
                {
                  left: `${startRect.left}px`,
                  top: `${startRect.top}px`,
                  width: `${startRect.width}px`,
                  height: `${startRect.height}px`,
                },
                {
                  left: `${endRect.left}px`,
                  top: `${endRect.top}px`,
                  width: `${endRect.width}px`,
                  height: `${endRect.height}px`,
                },
              ],
              { duration: 720, easing: "cubic-bezier(.22,1,.36,1)", fill: "forwards" }
            );

            let done = false;
            const finish = () => {
              if (done) return;
              done = true;
              animation.cancel();
              composerShell.classList.remove("composer-floating");
              composerShell.style.position = "";
              composerShell.style.left = "";
              composerShell.style.top = "";
              composerShell.style.width = "";
              composerShell.style.height = "";
              dockSlot.appendChild(composerShell);
              introSlot.style.minHeight = "";
              app.classList.remove("is-transitioning");
              app.classList.add("is-chatting");
              isTransitioning = false;
              updateDockMetrics();
              requestAnimationFrame(() => showComposerHint());
              toggleSendState();
              resolve();
            };

            animation.addEventListener("finish", finish, { once: true });
            setTimeout(finish, 820);
          });
        });
      }

      function resetComposerToIntro() {
        document.getElementById("dock")?.classList.remove("dock-fading");
        const oldGhost = introSlot.querySelector(".intro-return-ghost");
        if (oldGhost) oldGhost.remove();
        introSlot.appendChild(composerShell);
        composerShell.classList.remove("composer-floating", "is-chat-layout");
        clearComposerInlineMotion();
        introSlot.style.minHeight = "";
        app.classList.remove("is-transitioning", "is-chatting", "is-returning", "is-intro-revealing", "is-closing", "is-intro-locked");
        setPlaceholderImmediate("");
        typePlaceholder(INTRO_PLACEHOLDER, { delay: 120, speed: 38 });
        closeStarterDropdown();
        closeAttachMenu();
        autoResize();
        requestAnimationFrame(() => showComposerHint());
        toggleSendState();
        composerInput.focus();
      }

      function clearChat() {
        clearTimeout(typingTimeout);
        setRandomGreeting();
        isAwaitingResponse = false;
        isLockedUntilReplyFinishes = false;
        localStorage.removeItem(STORAGE_KEY);
        messages.innerHTML = "";
        composerInput.value = "";
        autoResize();
        if (typeof syncComposerTextState === "function") syncComposerTextState();
        closeStarterDropdown();
        closeAttachMenu();

        if (!isChatting() || isTransitioning) {
          isTransitioning = false;
          resetComposerToIntro();
          return;
        }

        isTransitioning = true;
        toggleSendState();
        hideComposerHint();
        fadeOutPlaceholder({ duration: 220 });

        /*
          Cierre estable:
          1) Se mide el prompt visible en el dock.
          2) El intro queda en layout real, con saludo/carousel/footer en opacity 0.
          3) Se inserta un ghost invisible en el slot del prompt para fijar el destino final.
          4) El prompt flota hasta ese rect exacto.
          5) Se reemplaza el ghost con el prompt real mientras está oculto un frame,
             se limpian estilos inline y recién ahí reaparecen los demás elementos.
        */
        const startRect = composerShell.getBoundingClientRect();
        const dock = document.getElementById("dock");
        dock?.classList.remove("dock-fading");
        dock?.classList.add("dock-hold");
        dock?.style.setProperty("--ps-dock-hold", `${Math.ceil(startRect.height)}px`);
        dockSlot.style.minHeight = `${Math.ceil(startRect.height)}px`;

        app.classList.remove("is-returning", "is-intro-revealing", "is-intro-locked", "is-closing-visible");
        app.classList.add("is-closing", "is-transitioning");

        requestAnimationFrame(() => {
          const ghost = createIntroComposerGhost();

          // Fijar el prompt visible en su punto de partida antes de revelar el intro.
          composerShell.classList.add("composer-floating", "is-chat-layout");
          composerShell.style.position = "fixed";
          composerShell.style.left = `${startRect.left}px`;
          composerShell.style.top = `${startRect.top}px`;
          composerShell.style.width = `${startRect.width}px`;
          composerShell.style.height = `${startRect.height}px`;
          document.body.appendChild(composerShell);

          // El layout de origen aparece primero. El ghost ya reserva el lugar exacto del prompt.
          void ghost.offsetHeight;
          app.classList.add("is-closing-visible");

          // Normalizar el estado final del input mientras el shell está fijo con alto explícito.
          normalizeComposerForIntroLayout();

          // El layout ya está reservado por el ghost. El fade de saludo/carousel y el retorno
          // del prompt arrancan juntos para que la escena se recomponga como una sola transición.
          requestAnimationFrame(() => {
            const endRect = getRectFromElement(ghost);
            composerShell.classList.remove("is-chat-layout");

            const animation = composerShell.animate(
              [
                {
                  left: `${startRect.left}px`,
                  top: `${startRect.top}px`,
                  width: `${startRect.width}px`,
                  height: `${startRect.height}px`,
                },
                {
                  left: `${endRect.left}px`,
                  top: `${endRect.top}px`,
                  width: `${endRect.width}px`,
                  height: `${endRect.height}px`,
                },
              ],
              { duration: 860, easing: "cubic-bezier(.22,1,.36,1)", fill: "forwards" }
            );

            let done = false;
            const finish = () => {
              if (done) return;
              done = true;

              animation.cancel();

              // Ocultar sólo el intercambio DOM para que no se vea el snap entre fixed y flow.
              composerShell.style.visibility = "hidden";
              composerShell.classList.remove("composer-floating", "is-chat-layout");
              clearComposerInlineMotion();
              normalizeComposerForIntroLayout();
              setPlaceholderImmediate("");

              if (ghost.parentNode) {
                ghost.replaceWith(composerShell);
              } else {
                introSlot.appendChild(composerShell);
              }

              app.classList.remove(
                "is-chatting",
                "is-closing",
                "is-closing-visible",
                "is-transitioning",
                "is-returning",
                "is-intro-locked",
                "is-intro-revealing"
              );
              closeStarterDropdown();
              closeAttachMenu();

              // Un frame para que el browser calcule el flow final antes de mostrar el prompt real.
              requestAnimationFrame(() => {
                introSlot.style.minHeight = "";
                autoResize();
                toggleSendState();
                composerInput.focus();

                requestAnimationFrame(() => {
                  composerShell.style.visibility = "";
                  typePlaceholder(INTRO_PLACEHOLDER, { delay: 120, speed: 38 });
                  showComposerHint();
                  setTimeout(() => {
                    dock?.classList.add("dock-fading");
                    setTimeout(() => {
                      dock?.classList.remove("dock-hold", "dock-fading");
                      dock?.style.removeProperty("--ps-dock-hold");
                      dockSlot.style.minHeight = "";
                    }, 780);
                  }, 2000);
                  isTransitioning = false;
                  toggleSendState();
                });
              });
            };

            animation.addEventListener("finish", finish, { once: true });
            setTimeout(finish, 980);
          });
        });
      }

// ─── Markdown mínimo: convierte [texto](url) en <a> clickeable ───────────

      function renderMarkdown(text) {
        const div = document.createElement("div");

        // Escapar HTML base
        let safe = text
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");

        // [texto](url) → <a href="url" target="_blank">texto</a>
        safe = safe.replace(
          /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g,
          '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // URLs crudas sueltas → mostrar solo el hostname como texto
        safe = safe.replace(
          /(?<!\()(https?:\/\/[^\s<"&]+)/g,
          (url) => {
            try { return new URL(url).hostname; }
            catch { return ""; }
          }
        );

        // Saltos de línea → <br>
        safe = safe.replace(/\n/g, "<br>");

        div.innerHTML = safe;
        return div;
      }

      // ─── Comunicación con n8n ─────────────────────────────────────────────────

      async function showTypingAndReply(userText) {
        isAwaitingResponse = true;
        toggleSendState();

        const typingRow = appendMessage("assistant", "", { typing: true });

        try {
          const resp = await fetch(N8N_WEBHOOK_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: userText }),
          });

          const raw = await resp.text();

          if (!resp.ok) {
            throw new Error(`HTTP ${resp.status} - ${raw || "sin body"}`);
          }

          if (!raw.trim()) {
            throw new Error("n8n respondió 200 pero con body vacío");
          }

          let data;
          try {
            data = JSON.parse(raw);
          } catch {
            throw new Error(`La respuesta no es JSON: ${raw}`);
          }

          const result = Array.isArray(data) ? data[0] : data;
          const replyText =
            result.reply || result.output || result.text || result.response || "Sin respuesta.";

          typingRow.remove();

          // Crear fila con contenido renderizado (markdown → HTML)
          const row = document.createElement("div");
          row.className = "message-row assistant";
          const bubble = document.createElement("div");
          bubble.className = "message-bubble";
          bubble.appendChild(renderMarkdown(replyText));
          row.appendChild(bubble);
          messages.appendChild(row);
          scrollToBottom();

        } catch (err) {
          console.error("Error real contra n8n:", err);
          typingRow.remove();
          appendMessage("assistant", `Error conectando con n8n: ${err.message}`);
        }

        saveMessages();
        isAwaitingResponse = false;
        isLockedUntilReplyFinishes = false;
        toggleSendState();
      }

// ─── Submit del prompt ────────────────────────────────────────────────────

      async function submitPrompt() {
        const text = composerInput.value.trim();
        if (!text || isAwaitingResponse || isTransitioning || isLockedUntilReplyFinishes) return;

        isLockedUntilReplyFinishes = true;
        toggleSendState();
        closeStarterDropdown();
        closeAttachMenu();

        appendMessage("user", text);
        saveMessages();
        composerInput.value = "";
        autoResize();
        if (typeof syncComposerTextState === "function") syncComposerTextState();

        if (!isChatting()) {
          await transitionToChatMode();
          scrollToBottom();
        } else {
          setPlaceholderImmediate(CHAT_PLACEHOLDER);
        }

        composerInput.focus();
        await showTypingAndReply(text);
        toggleSendState();
      }

      // ─── Event listeners ──────────────────────────────────────────────────────

      composerForm.addEventListener("submit", (event) => {
        event.preventDefault();
        submitPrompt();
      });

      function syncComposerTextState() {
        composerForm.classList.toggle("has-text", Boolean(composerInput.value.trim()));
      }

      composerInput.addEventListener("input", () => {
        autoResize();
        syncComposerTextState();
        toggleSendState();
      });

      composerInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          submitPrompt();
        }
      });

      starterButtons.forEach((button) => {
        button.addEventListener("click", () => {
          if (isChatting() || isTransitioning) return;
          toggleStarterDropdown(button.dataset.group);
        });
      });

      starterDropdownClose.addEventListener("click", closeStarterDropdown);

      attachBtn.addEventListener("click", () => {
        if (isTransitioning) return;
        toggleAttachMenu();
      });

      attachItems.forEach((item) => {
        item.addEventListener("click", () => {
          const type = item.dataset.attach;
          const prefix = type === "imagen" ? "[Imagen] " : type === "archivo" ? "[Archivo] " : "[Documento] ";
          const current = composerInput.value.trim();
          composerInput.value = current ? `${current} ${prefix}` : prefix;
          autoResize();
          if (typeof syncComposerTextState === "function") syncComposerTextState();
          toggleSendState();
          closeAttachMenu();
          composerInput.focus();
          composerInput.setSelectionRange(composerInput.value.length, composerInput.value.length);
        });
      });

      clearBtn.addEventListener("click", clearChat);

      document.addEventListener("click", (event) => {
        if (!composerShell.contains(event.target)) {
          closeAttachMenu();
        }

        const insideStarter =
          starterDropdown.contains(event.target) ||
          starterButtons.some((button) => button.contains(event.target));
        if (!insideStarter) {
          closeStarterDropdown();
        }
      });

      window.addEventListener("resize", () => {
        updateDockMetrics();
        scheduleComposerHintUpdate();
        if (!isChatting() && !isTransitioning) return;
        scrollToBottom();
      });

      // ─── Init ─────────────────────────────────────────────────────────────────

      setRandomGreeting();
      loadMessages();
      if (!isChatting()) {
        setPlaceholderImmediate("");
        typePlaceholder(INTRO_PLACEHOLDER, { delay: 180, speed: 38 });
      }
      if (typeof syncComposerTextState === "function") syncComposerTextState();
      updateDockMetrics();
      requestAnimationFrame(() => showComposerHint({ immediate: true }));
      window.addEventListener("load", () => {
        updateDockMetrics();
        scheduleComposerHintUpdate();
      });

// Carousel de sugeridos: al hacer click completa el prompt, no envía automáticamente.
      function imgFallback(img, kind) {
        const wrap = img?.parentElement;
        if (!wrap) return;
        const glyphs = {
          person: '<circle cx="60" cy="46" r="20"/><path d="M26 104c0-19 15-32 34-32s34 13 34 32" fill="none" stroke="currentColor" stroke-width="6"/>',
          doc: '<rect x="34" y="26" width="52" height="68" rx="6" fill="none" stroke="currentColor" stroke-width="6"/><path d="M46 46h28M46 60h28M46 74h18" stroke="currentColor" stroke-width="6" stroke-linecap="round"/>',
          chart: '<path d="M30 90V58M52 90V40M74 90V52M96 90V32" stroke="currentColor" stroke-width="7" stroke-linecap="round" fill="none"/>'
        };
        wrap.innerHTML = '<div class="media-fallback"><svg viewBox="0 0 120 120" width="64" height="64" fill="currentColor">' + (glyphs[kind] || glyphs.doc) + '</svg></div>';
      }

      (function initPersonalStockCarousel() {
        const car = document.getElementById("carousel");
        if (!car) return;
        const prev = document.getElementById("prev");
        const next = document.getElementById("next");
        const cards = Array.from(car.querySelectorAll(".card"));
        const step = () => Math.min(car.clientWidth * 0.8, 360);

        function updateFade() {
          const max = Math.max(0, car.scrollWidth - car.clientWidth);
          const left = car.scrollLeft;
          const right = max - left;
          car.style.setProperty("--fade-l", left > 4 ? "48px" : "0px");
          car.style.setProperty("--fade-r", right > 4 ? "48px" : "0px");
        }

        prev?.addEventListener("click", () => car.scrollBy({ left: -step(), behavior: "smooth" }));
        next?.addEventListener("click", () => car.scrollBy({ left: step(), behavior: "smooth" }));
        car.addEventListener("scroll", updateFade, { passive: true });
        window.addEventListener("resize", updateFade);
        requestAnimationFrame(updateFade);

        let isDown = false;
        let startX = 0;
        let startScroll = 0;
        let moved = false;

        car.addEventListener("pointerdown", (event) => {
          isDown = true;
          moved = false;
          startX = event.pageX;
          startScroll = car.scrollLeft;
          // No activamos .dragging ni pointer-capture acá: si se hace en pointerdown,
          // el click de la card puede perderse antes de copiar el texto al prompt.
        });

        car.addEventListener("pointermove", (event) => {
          if (!isDown) return;
          const dx = event.pageX - startX;
          if (Math.abs(dx) > 4) {
            moved = true;
            car.classList.add("dragging");
            car.setPointerCapture?.(event.pointerId);
            car.scrollLeft = startScroll - dx;
          }
        });

        function stopDrag(event) {
          if (!isDown) return;
          isDown = false;
          car.classList.remove("dragging");
          if (event?.pointerId !== undefined) car.releasePointerCapture?.(event.pointerId);
        }

        car.addEventListener("pointerup", stopDrag);
        car.addEventListener("pointercancel", stopDrag);
        car.addEventListener("pointerleave", stopDrag);

        function pasteCardPrompt(card) {
          const prompt = (card.dataset.prompt || "").trim();
          if (!prompt) return;

          cards.forEach((item) => item.classList.remove("active"));
          card.classList.add("active");

          composerInput.value = prompt;
          composerInput.dispatchEvent(new Event("input", { bubbles: true }));
          if (typeof autoResize === "function") autoResize();
          if (typeof toggleSendState === "function") toggleSendState();

          composerInput.focus({ preventScroll: true });
          const end = composerInput.value.length;
          composerInput.setSelectionRange(end, end);
        }

        cards.forEach((card) => {
          card.addEventListener("click", (event) => {
            if (moved || isTransitioning || isChatting()) return;
            event.preventDefault();
            event.stopPropagation();
            pasteCardPrompt(card);
          });
        });
      })();

// Layout agregado: sidebar, topbar, menú de usuario y switch de tema.
      (function initPersonalStockLayout() {
        const sidebar = document.getElementById("sidebar");
        const menuToggle = document.getElementById("menuToggle");
        const user = document.getElementById("user");
        const userBtn = document.getElementById("userBtn");
        const dropdown = document.getElementById("dropdown");
        const themeBtn = document.getElementById("themeToggle");
        const brandLogo = document.getElementById("brandLogo");
        const sideNewChat = document.getElementById("sideNewChat");
        const newChatBtn = document.getElementById("newChatBtn");
        const themeStorageKey = "personal-stock-theme";

        function syncSidebarState() {
          document.body.classList.toggle("sidebar-open", Boolean(sidebar?.classList.contains("show")));
        }

        function closeSidebarOnMobile() {
          if (window.matchMedia("(max-width: 920px)").matches) {
            sidebar?.classList.remove("show");
            syncSidebarState();
          }
        }

        document.querySelectorAll(".nav-item[data-sub]").forEach((item) => {
          item.addEventListener("click", () => {
            const submenu = document.getElementById(item.dataset.sub);
            const willOpen = !item.classList.contains("open");

            document.querySelectorAll(".nav-item[data-sub]").forEach((other) => {
              other.classList.remove("open", "active");
              const otherSubmenu = document.getElementById(other.dataset.sub);
              otherSubmenu?.classList.remove("open");
            });

            if (willOpen) {
              item.classList.add("open", "active");
              submenu?.classList.add("open");
            } else {
              item.classList.add("active");
            }
          });
        });

        menuToggle?.addEventListener("click", (event) => {
          event.stopPropagation();
          sidebar?.classList.toggle("show");
          syncSidebarState();
        });

        userBtn?.addEventListener("click", (event) => {
          event.stopPropagation();
          const isOpen = dropdown?.classList.toggle("open");
          user?.classList.toggle("open", Boolean(isOpen));
          userBtn.setAttribute("aria-expanded", String(Boolean(isOpen)));
        });

        document.addEventListener("click", (event) => {
          if (user && !user.contains(event.target)) {
            dropdown?.classList.remove("open");
            user.classList.remove("open");
            userBtn?.setAttribute("aria-expanded", "false");
          }

          if (sidebar && menuToggle && !sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
            closeSidebarOnMobile();
          }
        });

        window.addEventListener("resize", () => {
          if (!window.matchMedia("(max-width: 920px)").matches) {
            sidebar?.classList.remove("show");
            syncSidebarState();
          }
        });

        document.addEventListener("keydown", (event) => {
          if (event.key === "Escape") {
            sidebar?.classList.remove("show");
            syncSidebarState();
            dropdown?.classList.remove("open");
            user?.classList.remove("open");
            userBtn?.setAttribute("aria-expanded", "false");
          }
        });

        let themeFadeTimeout = null;

        function applyTheme(light, animate = false) {
          if (animate) {
            clearTimeout(themeFadeTimeout);
            document.body.classList.add("theme-ready", "theme-fading");
          }

          document.body.classList.toggle("light", light);
          themeBtn?.setAttribute("aria-checked", String(light));

          try {
            localStorage.setItem(themeStorageKey, light ? "light" : "dark");
          } catch {}

          if (animate) {
            themeFadeTimeout = setTimeout(() => {
              document.body.classList.remove("theme-fading");
            }, 900);
          }
        }

        let savedTheme = null;
        try {
          savedTheme = localStorage.getItem(themeStorageKey);
        } catch {}
        applyTheme(savedTheme === "light" || document.body.classList.contains("light"), false);
        requestAnimationFrame(() => document.body.classList.add("theme-ready"));

        themeBtn?.addEventListener("click", () => {
          applyTheme(!document.body.classList.contains("light"), true);
        });

        [sideNewChat, newChatBtn].forEach((button) => {
          button?.addEventListener("click", () => {
            closeSidebarOnMobile();
            if (typeof clearChat === "function") clearChat();
          });
        });
      })();

// Fallbacks de imagen desacoplados del HTML.
document.querySelectorAll("img[data-fallback]").forEach((img) => {
  const applyFallback = () => imgFallback(img, img.dataset.fallback || "doc");
  img.addEventListener("error", applyFallback, { once: true });
  if (img.complete && img.naturalWidth === 0) applyFallback();
});
