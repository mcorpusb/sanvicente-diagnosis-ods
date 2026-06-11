/* ============================================================
   Dashboard de Diagnosis — main.js
   ============================================================ */

"use strict";

/* ---- Toast notifications ---- */
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast toast--${type} show`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.classList.remove("show"); }, 4000);
}

/* ---- Escape HTML to avoid XSS ---- */
function escHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ---- Populate history table ---- */
function renderHistory(records) {
  const loadingEl = document.getElementById("loadingHistory");
  const emptyEl   = document.getElementById("emptyHistory");
  const wrapperEl = document.getElementById("historyTableWrapper");
  const tbody     = document.getElementById("historyBody");

  if (!loadingEl || !emptyEl || !wrapperEl || !tbody) return;

  loadingEl.style.display = "none";

  if (!records || records.length === 0) {
    emptyEl.style.display  = "block";
    wrapperEl.style.display = "none";
    return;
  }

  emptyEl.style.display   = "none";
  wrapperEl.style.display = "block";

  tbody.innerHTML = records
    .slice()
    .reverse()
    .map((r) => {
      const codes = (r.fault_codes || [])
        .map((c) => `<span class="badge">${escHtml(c)}</span>`)
        .join(" ");
      return `
        <tr>
          <td><code>${escHtml(r.record_id || "—")}</code></td>
          <td style="white-space:nowrap">${escHtml(r.timestamp || "")}</td>
          <td><strong>${escHtml(r.vehicle_id)}</strong></td>
          <td>${escHtml(r.make)} ${escHtml(r.model)} (${escHtml(r.year)})</td>
          <td>${escHtml(r.technician)}</td>
          <td>${codes || "—"}</td>
          <td class="cell-truncate" title="${escHtml(r.ai_diagnosis || "")}">${escHtml(r.ai_diagnosis || "—")}</td>
        </tr>`;
    })
    .join("");
}

/* ---- Load records from API ---- */
async function loadHistory() {
  const loadingEl = document.getElementById("loadingHistory");
  if (loadingEl) loadingEl.style.display = "block";

  try {
    const resp = await fetch("/api/records");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const records = await resp.json();
    renderHistory(records);
  } catch (err) {
    console.error("Error cargando historial:", err);
    const loadingEl2 = document.getElementById("loadingHistory");
    if (loadingEl2) loadingEl2.textContent = "No se pudo cargar el historial.";
    showToast("Error al cargar el historial.", "error");
  }
}

/* ---- Show diagnosis result ---- */
function showResult(data) {
  const card  = document.getElementById("resultCard");
  const meta  = document.getElementById("resultMeta");
  const diagEl = document.getElementById("resultDiagnosis");
  const recEl  = document.getElementById("resultRecommendations");

  if (!card) return;

  meta.innerHTML = `
    <span>🚗 ${escHtml(data.make)} ${escHtml(data.model)} ${escHtml(data.year)}</span>
    <span>📋 ${escHtml(data.vehicle_id)}</span>
    <span>🔧 ${escHtml(data.technician)}</span>
    <span>🕐 ${escHtml(data.timestamp)}</span>
    ${data.record_id ? `<span>🆔 ${escHtml(data.record_id)}</span>` : ""}
  `;

  diagEl.textContent = data.ai_diagnosis || "Sin diagnóstico.";
  recEl.textContent  = data.ai_recommendations || "Sin recomendaciones.";

  card.style.display = "block";
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ---- Form submission ---- */
async function handleSubmit(event) {
  event.preventDefault();
  const form      = event.target;
  const submitBtn = document.getElementById("submitBtn");

  /* Basic validation */
  let valid = true;
  ["vehicle_id", "make", "model", "year", "mileage", "technician"].forEach((name) => {
    const el = form.elements[name];
    if (!el) return;
    if (!el.value.trim()) {
      el.classList.add("invalid");
      valid = false;
    } else {
      el.classList.remove("invalid");
    }
  });

  if (!valid) {
    showToast("Por favor, completa todos los campos obligatorios.", "error");
    return;
  }

  /* Disable button while loading */
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Analizando…';

  const payload = {
    vehicle_id:  form.elements["vehicle_id"].value.trim().toUpperCase(),
    make:        form.elements["make"].value.trim(),
    model:       form.elements["model"].value.trim(),
    year:        parseInt(form.elements["year"].value, 10),
    mileage:     parseInt(form.elements["mileage"].value, 10),
    fault_codes: form.elements["fault_codes"].value.trim(),
    symptoms:    form.elements["symptoms"].value.trim(),
    technician:  form.elements["technician"].value.trim(),
  };

  try {
    const resp = await fetch("/api/diagnose", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await resp.json();

    if (!resp.ok) {
      showToast(data.error || "Error al procesar el diagnóstico.", "error");
      return;
    }

    showResult(data);
    showToast("Diagnóstico completado y guardado. ✅", "success");
    await loadHistory();

  } catch (err) {
    console.error("Error en diagnose:", err);
    showToast("Error de conexión con el servidor.", "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span class="btn-icon">🤖</span> Diagnosticar con IA';
  }
}

/* ---- Clear form ---- */
function clearForm() {
  const form = document.getElementById("diagnosisForm");
  if (form) form.reset();
  document.querySelectorAll(".invalid").forEach((el) => el.classList.remove("invalid"));
  const resultCard = document.getElementById("resultCard");
  if (resultCard) resultCard.style.display = "none";
}

/* ---- Init ---- */
document.addEventListener("DOMContentLoaded", () => {
  const form      = document.getElementById("diagnosisForm");
  const clearBtn  = document.getElementById("clearBtn");
  const refreshBtn = document.getElementById("refreshBtn");

  if (form)       form.addEventListener("submit", handleSubmit);
  if (clearBtn)   clearBtn.addEventListener("click", clearForm);
  if (refreshBtn) refreshBtn.addEventListener("click", loadHistory);

  /* Remove invalid class on input */
  document.querySelectorAll("input, textarea").forEach((el) => {
    el.addEventListener("input", () => el.classList.remove("invalid"));
  });

  loadHistory();
});
