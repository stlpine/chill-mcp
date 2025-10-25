document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.querySelector(".status-indicator");
  const errorBanner = document.querySelector(".error-banner");
  const stressValue = document.querySelector('[data-metric="stress"][data-field="value"]');
  const stressBar = document.querySelector('[data-metric="stress"][data-field="bar"]');
  const bossValue = document.querySelector('[data-metric="boss"][data-field="value"]');
  const bossBar = document.querySelector('[data-metric="boss"][data-field="bar"]');
  const cooldownValue = document.querySelector('[data-metric="cooldown"][data-field="value"]');
  const eventsTimeline = document.querySelector('[data-events="timeline"]');

  async function fetchState() {
    try {
      const response = await fetch("/api/state", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      updateDashboard(data);
    } catch (error) {
      console.error("Failed to fetch state", error);
      showError("웹 서버가 MCP 상태를 불러오지 못했습니다. 잠시 후 다시 시도하세요.");
      setStatus("offline", "MCP Offline");
    }
  }

  function setStatus(status, label) {
    statusEl.dataset.status = status;
    statusEl.querySelector("strong").textContent = label;
  }

  function showError(message) {
    errorBanner.dataset.visible = "true";
    errorBanner.textContent = message;
  }

  function hideError() {
    errorBanner.dataset.visible = "false";
    errorBanner.textContent = "";
  }

  function updateDashboard(payload) {
    const { status } = payload;
    if (status === "ok") {
      hideError();
      setStatus("ok", "MCP Online");
    } else if (status === "degraded") {
      showError("MCP 서버 응답이 지연되고 있습니다. 최신 상태가 아닐 수 있어요.");
      setStatus("degraded", "MCP Degraded");
    } else {
      showError(payload.error ?? "MCP 서버에 연결할 수 없습니다.");
      setStatus("offline", "MCP Offline");
    }

    if (!payload.snapshot) {
      return;
    }

    const snapshot = payload.snapshot;
    stressValue.textContent = `${snapshot.stress_level} / 100`;
    stressBar.style.width = `${Math.min(100, Math.max(0, snapshot.stress_level))}%`;

    bossValue.textContent = `${snapshot.boss_alert_level} / 5`;
    const bossPercent = (snapshot.boss_alert_level / 5) * 100;
    bossBar.style.width = `${Math.min(100, Math.max(0, bossPercent))}%`;

    const cooldownSeconds = Math.round(snapshot.cooldown_seconds_remaining);
    cooldownValue.textContent = `${cooldownSeconds}s`;

    refreshEvents();
  }

  function formatRelative(isoString) {
    if (!isoString) return "-";
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.round(diffMs / 1000);
      if (diffSec < 60) return `${diffSec}s ago`;
      const diffMin = Math.round(diffSec / 60);
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHour = Math.round(diffMin / 60);
      if (diffHour < 24) return `${diffHour}h ago`;
      return date.toLocaleString();
    } catch (error) {
      console.warn("Failed to format time", error);
      return isoString;
    }
  }

  fetchState();
  setInterval(fetchState, 4000);

  async function refreshEvents() {
    if (!eventsTimeline) return;
    try {
      const response = await fetch('/api/events', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const { events } = await response.json();
      renderTimeline(events ?? []);
    } catch (error) {
      console.warn('Failed to refresh events', error);
    }
  }

  function renderTimeline(events) {
    eventsTimeline.innerHTML = '';
    if (!events || events.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'timeline-item';
      empty.innerHTML = '<strong>이력이 없습니다</strong><time>-</time>';
      eventsTimeline.appendChild(empty);
      return;
    }

    events.slice(0, 4).forEach((event) => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      const title = document.createElement('strong');
      title.textContent = `${event.emoji ?? ''} ${event.label ?? event.tool}`.trim();
      const message = document.createElement('div');
      message.textContent = event.break_summary || event.message || '';
      const time = document.createElement('time');
      time.dateTime = event.timestamp;
      time.textContent = formatRelative(event.timestamp);

      item.appendChild(title);
      if (message.textContent) {
        item.appendChild(message);
      }
      item.appendChild(time);
      eventsTimeline.appendChild(item);
    });
  }

  refreshEvents();
  setInterval(refreshEvents, 6000);
});
