const API_BASE = "";

const totalEl = document.getElementById("total-alerts");
const ackEl = document.getElementById("ack-alerts");
const unackEl = document.getElementById("unack-alerts");
const visibleEl = document.getElementById("visible-alerts");
const alertsBody = document.getElementById("alerts-body");
const filterEl = document.getElementById("filter");
const searchEl = document.getElementById("search");
const refreshBtn = document.getElementById("refresh-btn");
const lastRefreshEl = document.getElementById("last-refresh");
const errorBox = document.getElementById("error-box");

// Acknowledge modal
const ackModal = document.getElementById("ack-modal");
const ackModalAlertId = document.getElementById("ack-modal-alert-id");
const ackByInput = document.getElementById("ack-by");
const ackNoteInput = document.getElementById("ack-note");
const ackSubmitBtn = document.getElementById("ack-submit");
const ackCancelBtn = document.getElementById("ack-cancel");
const ackError = document.getElementById("ack-error");

// Detail panel
const detailPanel = document.getElementById("detail-panel");
const detailContent = document.getElementById("detail-content");
const detailCloseBtn = document.getElementById("detail-close");

let currentAlerts = [];
let selectedAlertId = null;

// ── UI helpers ─────────────────────────────────────────────────────────────

function showError(message) {
  errorBox.style.display = "block";
  errorBox.textContent = message;
}

function clearError() {
  errorBox.style.display = "none";
  errorBox.textContent = "";
}

function fmtAck(value) {
  return value
    ? `<span class="badge badge-ack">Acknowledged</span>`
    : `<span class="badge badge-unack">Unacknowledged</span>`;
}

function fmtStatus(value) {
  return `<span class="badge badge-alert">${escapeHtml(value || "Unknown")}</span>`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Table rendering ────────────────────────────────────────────────────────

function applyTableFilter() {
  const search = searchEl.value.trim().toLowerCase();

  const filtered = currentAlerts.filter(item => {
    const haystack = [
      item.alert_id,
      item.metric,
      item.device_id,
      item.asset_type,
      item.status
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return haystack.includes(search);
  });

  visibleEl.textContent = filtered.length;

  if (!filtered.length) {
    alertsBody.innerHTML = `<tr class="state-row"><td colspan="9" class="muted">No alerts match the current filter.</td></tr>`;
    return;
  }

  alertsBody.innerHTML = filtered.map(item => {
    const isUnack = !item.acknowledged;
    const ackBtnHtml = isUnack
      ? `<button class="button button-success" style="padding:6px 10px;font-size:12px" onclick="openAckModal('${escapeHtml(item.alert_id || "")}')">Acknowledge</button>`
      : `<button class="button" style="padding:6px 10px;font-size:12px" onclick="openDetailPanel('${escapeHtml(item.alert_id || "")}')">View</button>`;

    return `
      <tr data-alert-id="${escapeHtml(item.alert_id || "")}" style="cursor:pointer">
        <td class="time-cell">${escapeHtml(item.time || "-")}</td>
        <td class="id-cell">${escapeHtml(item.alert_id || "-")}</td>
        <td>${escapeHtml(item.metric || "-")}</td>
        <td>${escapeHtml(String(item.value ?? "-"))}</td>
        <td>${fmtStatus(item.status)}</td>
        <td>${fmtAck(item.acknowledged)}</td>
        <td>${escapeHtml(item.device_id || "-")}</td>
        <td>${escapeHtml(item.asset_type || "-")}</td>
        <td>${ackBtnHtml}</td>
      </tr>
    `;
  }).join("");

  // Row click opens detail panel (not on button click)
  alertsBody.querySelectorAll("tr[data-alert-id]").forEach(row => {
    row.addEventListener("click", e => {
      if (e.target.tagName === "BUTTON") return;
      openDetailPanel(row.dataset.alertId);
    });
  });
}

// ── Detail panel ───────────────────────────────────────────────────────────

function openDetailPanel(alertId) {
  const item = currentAlerts.find(a => a.alert_id === alertId);
  if (!item) return;

  const fields = [
    ["Alert ID", item.alert_id],
    ["Time", item.time],
    ["Metric", item.metric],
    ["Value", item.value],
    ["Status", item.status],
    ["Device ID", item.device_id],
    ["Asset Type", item.asset_type],
    ["Acknowledged", item.acknowledged ? "Yes" : "No"],
    ["Acknowledged by", item.acknowledged_by],
    ["Acknowledged at", item.acknowledged_at],
    ["Incident note", item.incident_note],
    ["Message", item.message],
  ].filter(([, v]) => v !== undefined && v !== null && v !== "");

  detailContent.innerHTML = `
    <div class="detail-grid">
      ${fields.map(([label, value]) => `
        <div>
          <div class="detail-item-label">${escapeHtml(label)}</div>
          <div class="detail-item-value">${escapeHtml(String(value))}</div>
        </div>
      `).join("")}
    </div>
    ${!item.acknowledged ? `
      <div style="margin-top:16px">
        <button class="button button-success" onclick="openAckModal('${escapeHtml(item.alert_id || "")}')">Acknowledge this alert</button>
      </div>
    ` : ""}
  `;

  detailPanel.classList.add("active");
  detailPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

detailCloseBtn.addEventListener("click", () => {
  detailPanel.classList.remove("active");
});

// ── Acknowledge modal ──────────────────────────────────────────────────────

function openAckModal(alertId) {
  selectedAlertId = alertId;
  ackModalAlertId.textContent = alertId;
  ackByInput.value = "";
  ackNoteInput.value = "";
  ackError.style.display = "none";
  ackModal.classList.add("active");
  ackByInput.focus();
}

ackCancelBtn.addEventListener("click", () => {
  ackModal.classList.remove("active");
  selectedAlertId = null;
});

ackModal.addEventListener("click", e => {
  if (e.target === ackModal) {
    ackModal.classList.remove("active");
    selectedAlertId = null;
  }
});

ackSubmitBtn.addEventListener("click", submitAck);

async function submitAck() {
  const by = ackByInput.value.trim();
  if (!by) {
    ackError.textContent = "Acknowledged by is required.";
    ackError.style.display = "block";
    return;
  }

  ackSubmitBtn.disabled = true;
  ackSubmitBtn.textContent = "Saving…";
  ackError.style.display = "none";

  try {
    const body = { acknowledged_by: by };
    const note = ackNoteInput.value.trim();
    if (note) body.incident_note = note;

    const res = await fetch(`${API_BASE}/alerts/${encodeURIComponent(selectedAlertId)}/acknowledge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || `Server error ${res.status}`);
    }

    ackModal.classList.remove("active");
    selectedAlertId = null;
    await refreshAll();
  } catch (err) {
    ackError.textContent = `Acknowledgement failed: ${err.message}`;
    ackError.style.display = "block";
  } finally {
    ackSubmitBtn.disabled = false;
    ackSubmitBtn.textContent = "Confirm";
  }
}

// ── Data fetching ──────────────────────────────────────────────────────────

async function loadSummary() {
  const res = await fetch(`${API_BASE}/summary`);
  if (!res.ok) throw new Error("Failed to load summary");
  const data = await res.json();

  totalEl.textContent = data.total_alerts ?? "-";
  ackEl.textContent = data.acknowledged_alerts ?? "-";
  unackEl.textContent = data.unacknowledged_alerts ?? "-";
}

async function loadAlerts() {
  let url = `${API_BASE}/alerts?limit=50`;
  const filter = filterEl.value;
  if (filter === "true" || filter === "false") {
    url += `&acknowledged=${filter}`;
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load alerts");
  const data = await res.json();

  currentAlerts = data.items || [];
  applyTableFilter();
}

async function refreshAll() {
  clearError();
  alertsBody.innerHTML = `<tr class="state-row"><td colspan="9" class="muted">Loading alerts…</td></tr>`;
  visibleEl.textContent = "-";
  detailPanel.classList.remove("active");

  try {
    await Promise.all([loadSummary(), loadAlerts()]);
    lastRefreshEl.textContent = new Date().toLocaleString();
  } catch (err) {
    showError(`Dashboard refresh failed: ${err.message}`);
    alertsBody.innerHTML = `<tr class="state-row"><td colspan="9" class="muted">Unable to load alert data. Is the API service running?</td></tr>`;
  }
}

// ── Event listeners ────────────────────────────────────────────────────────

refreshBtn.addEventListener("click", refreshAll);
filterEl.addEventListener("change", loadAlerts);
searchEl.addEventListener("input", applyTableFilter);

// ── Initial load ───────────────────────────────────────────────────────────

refreshAll();
