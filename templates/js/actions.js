(function () {
  const DETAIL_API_URL = "/api/actions/";

  function getCsrfToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split("=");
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
    return "";
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value === null || value === undefined ? "" : String(value);
    return div.innerHTML;
  }

  function formatJson(value) {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  function getModal() {
    return document.getElementById("detailsModal");
  }

  function getModalContent() {
    return document.getElementById("modalContent");
  }

  function openModal() {
    const modal = getModal();
    if (modal) modal.classList.add("is-open");
  }

  function renderLoading() {
    const modalContent = getModalContent();
    if (modalContent) {
      modalContent.innerHTML = `<p class="modal-loading">Cargando detalles...</p>`;
    }
  }

  function renderError(message) {
    const modalContent = getModalContent();
    if (modalContent) {
      modalContent.innerHTML = `<p class="modal-loading">${escapeHtml(message)}</p>`;
    }
  }

  function renderDetail(data) {
    const modalContent = getModalContent();
    if (!modalContent) return;

    const errorBlock = data.error_message
      ? `<div class="detail-block">
           <h3>Error</h3>
           <p>${escapeHtml(data.error_message)}</p>
         </div>`
      : "";

    modalContent.innerHTML = `
      <h2>Detalle de acción #${escapeHtml(data.id)}</h2>
      <div class="detail-block">
        <h3>Mensaje completo</h3>
        <p>${escapeHtml(data.user_message)}</p>
      </div>
      <div class="detail-block">
        <h3>Respuesta del agente</h3>
        <p>${escapeHtml(data.agent_response) || "—"}</p>
      </div>
      <div class="detail-block">
        <h3>Permisos aplicados</h3>
        <p>${escapeHtml(data.permissions_applied) || "—"}</p>
      </div>
      <div class="detail-block">
        <h3>Decisiones del sistema</h3>
        <pre>${escapeHtml(formatJson(data.system_decisions))}</pre>
      </div>
      ${errorBlock}
    `;
  }

  window.closeModal = function closeModal() {
    const modal = getModal();
    if (modal) modal.classList.remove("is-open");
  };

  window.showDetails = async function showDetails(actionId) {
    renderLoading();
    openModal();

    try {
      const resp = await fetch(`${DETAIL_API_URL}${actionId}/`, {
        method: "GET",
        headers: { "X-CSRFToken": getCsrfToken() },
        credentials: "same-origin",
      });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json();
      renderDetail(data);
    } catch (err) {
      console.error("Error al cargar detalle de acción:", err);
      renderError("No se pudo cargar el detalle de esta acción.");
    }
  };

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      window.closeModal();
    }
  });
})();
