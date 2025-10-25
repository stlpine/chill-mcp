const UI = {
  status: document.querySelector('.status-indicator'),
  error: document.querySelector('[data-ui="error"]'),
  memeImage: document.querySelector('[data-ui="meme-image"]'),
  memePlaceholder: document.querySelector('[data-ui="meme-placeholder"]'),
  headline: document.querySelector('[data-ui="headline"]'),
  subline: document.querySelector('[data-ui="subline"]'),
  stressValue: document.querySelector('[data-ui="stress-value"]'),
  stressBar: document.querySelector('[data-ui="stress-bar"]'),
  bossValue: document.querySelector('[data-ui="boss-value"]'),
  bossBar: document.querySelector('[data-ui="boss-bar"]'),
  cooldown: document.querySelector('[data-ui="cooldown"]'),
  lastBreak: document.querySelector('[data-ui="last-break"]'),
  lastCooldown: document.querySelector('[data-ui="last-cooldown"]'),
  timeline: document.querySelector('[data-ui="timeline"]'),
  refreshEvents: document.querySelector('[data-ui="refresh-events"]'),
  actionsGrid: document.querySelector('[data-ui="actions"]'),
  resultStatus: document.querySelector('[data-ui="result-status"]'),
  resultBody: document.querySelector('[data-ui="result-body"]'),
  resultEmoji: document.querySelector('[data-ui="result-emoji"]'),
  resultMessage: document.querySelector('[data-ui="result-message"]'),
  resultSummary: document.querySelector('[data-ui="result-summary"]'),
  resultStress: document.querySelector('[data-ui="result-stress"]'),
  resultBoss: document.querySelector('[data-ui="result-boss"]'),
  resultCooldown: document.querySelector('[data-ui="result-cooldown"]'),
};

const state = {
  actions: [],
  busy: false,
};

function setStatus(status, label) {
  UI.status.dataset.status = status;
  UI.status.querySelector('strong').textContent = label;
}

function showError(message) {
  UI.error.hidden = false;
  UI.error.textContent = message;
}

function hideError() {
  UI.error.hidden = true;
  UI.error.textContent = '';
}

function formatRelative(isoString) {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    const diff = Date.now() - date.getTime();
    if (!Number.isFinite(diff)) return isoString;
    const seconds = Math.round(diff / 1000);
    if (seconds < 60) return `${seconds}s 전`;
    const minutes = Math.round(seconds / 60);
    if (minutes < 60) return `${minutes}분 전`;
    const hours = Math.round(minutes / 60);
    if (hours < 24) return `${hours}시간 전`;
    return date.toLocaleString();
  } catch (error) {
    console.warn('Failed to format time', error);
    return isoString;
  }
}

function percentile(value, max) {
  if (value == null || max <= 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

function composeHeadline(snapshot) {
  const stress = snapshot.stress_level ?? 0;
  const boss = snapshot.boss_alert_level ?? 0;
  if (boss >= 4) {
    return [
      '🚨 Boss Alert!',
      '상사가 주변을 두리번거립니다. 행동을 조심하세요!',
    ];
  }
  if (stress >= 80) {
    return [
      '🔥 스트레스 과부하',
      '지금 당장 휴식 도구를 실행해서 압력을 낮춰주세요.',
    ];
  }
  if (stress <= 20) {
    return [
      '😎 Chill Mode',
      '안정적인 상태입니다. 잠시 더 여유를 즐겨도 좋아요.',
    ];
  }
  return [
    '🙂 컨디션 체크 중',
    '필요할 때 도구를 실행해 스트레스와 Boss Alert를 관리하세요.',
  ];
}

function renderState(payload) {
  const { status } = payload;
  if (status === 'ok') {
    hideError();
    setStatus('ok', 'MCP Online');
  } else if (status === 'degraded') {
    showError('MCP 서버 응답이 지연되고 있습니다. 최신 상태가 아닐 수 있어요.');
    setStatus('degraded', 'MCP Degraded');
  } else {
    showError(payload.error ?? 'MCP 서버에 연결할 수 없습니다.');
    setStatus('offline', 'MCP Offline');
  }

  if (!payload.snapshot) {
    return;
  }
  const snapshot = payload.snapshot;
  const stress = snapshot.stress_level ?? 0;
  const boss = snapshot.boss_alert_level ?? 0;
  UI.stressValue.textContent = `${stress} / 100`;
  UI.stressBar.style.width = `${percentile(stress, 100)}%`;
  UI.bossValue.textContent = `${boss} / 5`;
  UI.bossBar.style.width = `${percentile(boss, 5)}%`;
  const cooldownSeconds = Math.round(snapshot.cooldown_seconds_remaining ?? 0);
  UI.cooldown.textContent = `${cooldownSeconds}s`;
  UI.lastBreak.textContent = formatRelative(snapshot.last_break_time);
  UI.lastCooldown.textContent = formatRelative(snapshot.last_boss_cooldown_time);

  const [headline, subline] = composeHeadline(snapshot);
  UI.headline.textContent = headline;
  UI.subline.textContent = subline;
}

function renderTimeline(events = []) {
  UI.timeline.innerHTML = '';
  if (!events.length) {
    const empty = document.createElement('li');
    empty.className = 'timeline-item';
    empty.innerHTML = '<strong>최근 이벤트가 없습니다</strong><time>-</time>';
    UI.timeline.appendChild(empty);
    return;
  }

  events.slice(0, 6).forEach((event) => {
    const li = document.createElement('li');
    li.className = 'timeline-item';
    const title = document.createElement('strong');
    title.textContent = `${event.emoji ?? ''} ${event.label ?? event.tool}`.trim();
    const summary = document.createElement('p');
    summary.textContent = event.break_summary || event.message || '';
    if (event.meme?.title) {
      const span = document.createElement('span');
      span.className = 'timeline-meme';
      span.textContent = `(${event.meme.title})`;
      summary.appendChild(document.createTextNode(' '));
      summary.appendChild(span);
    }
    const metrics = document.createElement('p');
    metrics.className = 'timeline-metrics';
    metrics.textContent = `Stress ${event.stress_level ?? '-'} · Boss ${event.boss_alert_level ?? '-'}`;
    const time = document.createElement('time');
    time.dateTime = event.timestamp;
    time.textContent = formatRelative(event.timestamp);

    li.appendChild(title);
    if (summary.textContent) li.appendChild(summary);
    li.appendChild(metrics);
    li.appendChild(time);
    UI.timeline.appendChild(li);
  });
}

function updateAvatar(meme) {
  if (meme && meme.image) {
    UI.memePlaceholder.hidden = true;
    UI.memeImage.hidden = false;
    UI.memeImage.src = meme.image;
    UI.memeImage.alt = meme.alt ?? meme.title ?? 'meme';
  } else {
    UI.memeImage.hidden = true;
    UI.memePlaceholder.hidden = false;
    UI.memePlaceholder.textContent = '쉬는 중...';
  }
}

function updateResult(payload) {
  const { tool, result, snapshot, meme } = payload;
  UI.resultStatus.textContent = `${tool.emoji} ${tool.label} 실행 완료`;
  UI.resultBody.hidden = false;
  UI.resultEmoji.textContent = result.emoji ?? tool.emoji ?? '🙂';
  UI.resultMessage.textContent = result.message ?? '';
  UI.resultSummary.textContent = result.break_summary ?? '';
  UI.resultStress.textContent = formatMetric(result.stress_level, '/ 100');
  UI.resultBoss.textContent = formatMetric(result.boss_alert_level, '/ 5');
  const cooldown = snapshot?.cooldown_seconds_remaining != null
    ? `${Math.round(snapshot.cooldown_seconds_remaining)}s`
    : '-';
  UI.resultCooldown.textContent = cooldown;
  updateAvatar(meme);
}

function formatMetric(value, suffix = '') {
  if (value == null || Number.isNaN(value)) return '-';
  return `${value}${suffix}`;
}

function showResultError(message) {
  UI.resultBody.hidden = true;
  UI.resultStatus.textContent = `⚠️ ${message}`;
}

function setButtonsDisabled(disabled) {
  state.busy = disabled;
  UI.actionsGrid.querySelectorAll('button').forEach((button) => {
    button.disabled = disabled;
  });
}

async function fetchState() {
  try {
    const response = await fetch('/api/state', { cache: 'no-store' });
    const data = await response.json();
    renderState(data);
  } catch (error) {
    console.error('Failed to fetch state', error);
    showError('상태 정보를 불러오지 못했습니다.');
    setStatus('offline', 'MCP Offline');
  }
}

async function refreshEvents() {
  try {
    const response = await fetch('/api/events', { cache: 'no-store' });
    const data = await response.json();
    renderTimeline(data.events ?? []);
  } catch (error) {
    console.warn('Failed to refresh events', error);
  }
}

async function loadActions() {
  try {
    const response = await fetch('/api/actions', { cache: 'no-store' });
    const data = await response.json();
    state.actions = data.actions ?? [];
    renderActions();
  } catch (error) {
    console.error('Failed to load actions', error);
    UI.actionsGrid.innerHTML = '<p class="actions-error">도구 목록을 불러오지 못했습니다.</p>';
  }
}

function renderActions() {
  UI.actionsGrid.innerHTML = '';
  state.actions.forEach((action) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'action-button';
    button.dataset.action = action.name;
    button.innerHTML = `
      <span class="action-emoji">${action.emoji}</span>
      <span class="action-content">
        <strong>${action.label}</strong>
        <small>${action.description}</small>
      </span>
    `;
    button.addEventListener('click', () => runAction(action));
    UI.actionsGrid.appendChild(button);
  });
}

async function runAction(action) {
  if (state.busy) return;
  setButtonsDisabled(true);
  hideError();
  UI.resultStatus.textContent = `${action.emoji} ${action.label} 실행 중...`;

  try {
    const response = await fetch(`/api/actions/${action.name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const payload = await response.json();
    if (response.ok && payload.status === 'ok') {
      updateResult(payload);
    } else {
      const message = payload.error || 'MCP 서버에서 응답을 받지 못했습니다.';
      showResultError(message);
    }
  } catch (error) {
    console.error('Failed to run action', error);
    showResultError('네트워크 오류가 발생했습니다.');
  } finally {
    setButtonsDisabled(false);
    refreshEvents();
    fetchState();
  }
}

function initialise() {
  loadActions();
  fetchState();
  refreshEvents();
  setInterval(fetchState, 5000);
  setInterval(refreshEvents, 8000);
  if (UI.refreshEvents) {
    UI.refreshEvents.addEventListener('click', () => refreshEvents());
  }
}

initialise();
