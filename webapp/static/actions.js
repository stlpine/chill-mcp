const actionsContainer = document.querySelector('[data-actions="list"]');
const resultStatus = document.querySelector('[data-result="status"]');
const resultBody = document.querySelector('[data-result="body"]');
const resultError = document.querySelector('[data-result="error"]');
const resultEmoji = document.querySelector('[data-result="emoji"]');
const resultMessage = document.querySelector('[data-result="message"]');
const resultSummary = document.querySelector('[data-result="summary"]');
const resultStress = document.querySelector('[data-result="stress"]');
const resultBoss = document.querySelector('[data-result="boss"]');
const resultCooldown = document.querySelector('[data-result="cooldown"]');
const eventsList = document.querySelector('[data-events="list"]');

async function loadActions() {
  try {
    const response = await fetch('/api/actions', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const { actions } = await response.json();
    renderActions(actions ?? []);
  } catch (error) {
    console.error('Failed to load actions', error);
    resultStatus.textContent = '도구 목록을 불러오지 못했습니다. 새로고침 후 다시 시도해주세요.';
  }
}

function renderActions(actions) {
  const fragment = document.createDocumentFragment();
  actions.forEach((action) => {
    const card = document.createElement('article');
    card.className = 'action-card';
    card.innerHTML = `
      <div class="action-meta">
        <span class="action-emoji">${action.emoji}</span>
        <strong>${action.label}</strong>
      </div>
      <p>${action.description}</p>
      <button type="button" data-action="${action.name}">실행하기</button>
    `;
    const button = card.querySelector('button');
    button.addEventListener('click', () => runAction(action, button));
    fragment.appendChild(card);
  });
  actionsContainer.innerHTML = '';
  actionsContainer.appendChild(fragment);
}

async function runAction(action, button) {
  button.disabled = true;
  showResultLoading(action);

  try {
    const response = await fetch(`/api/actions/${action.name}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const payload = await response.json().catch(() => ({}));

    if (response.ok && payload.status === 'ok') {
      updateResult(payload);
      await refreshEvents();
    } else {
      const message = payload.error || 'MCP 서버에서 응답을 받지 못했습니다.';
      showError(message);
    }
  } catch (error) {
    console.error('Failed to run action', error);
    showError('네트워크 오류가 발생했습니다. 잠시 후 다시 시도하세요.');
  } finally {
    button.disabled = false;
  }
}

function showResultLoading(action) {
  resultError.hidden = true;
  resultStatus.textContent = `${action.emoji} ${action.label} 실행 중...`;
  resultBody.hidden = true;
}

function updateResult(payload) {
  const { tool, result, snapshot } = payload;
  resultStatus.textContent = `${tool.emoji} ${tool.label} 실행 완료`;
  resultBody.hidden = false;
  resultError.hidden = true;

  resultEmoji.textContent = result.emoji ?? tool.emoji;
  resultMessage.textContent = result.message ?? '';
  resultSummary.textContent = result.break_summary ?? '';
  resultStress.textContent = formatMetric(result.stress_level, '/ 100');
  resultBoss.textContent = formatMetric(result.boss_alert_level, '/ 5');
  const cooldownText = snapshot?.cooldown_seconds_remaining != null
    ? `${Math.round(snapshot.cooldown_seconds_remaining)}s`
    : '-';
  resultCooldown.textContent = cooldownText;
}

function showError(message) {
  resultStatus.textContent = '⚠️ 도구 실행 실패';
  resultError.hidden = false;
  resultError.textContent = message;
  resultBody.hidden = true;
}

function formatMetric(value, suffix = '') {
  if (value == null || Number.isNaN(value)) return '-';
  return `${value}${suffix}`;
}

async function refreshEvents() {
  try {
    const response = await fetch('/api/events', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const { events } = await response.json();
    renderEvents(events ?? []);
  } catch (error) {
    console.warn('Failed to refresh events', error);
  }
}

function renderEvents(events) {
  eventsList.innerHTML = '';
  if (events.length === 0) {
    const li = document.createElement('li');
    li.textContent = '아직 기록된 이벤트가 없습니다.';
    eventsList.appendChild(li);
    return;
  }

  const fragment = document.createDocumentFragment();
  events.forEach((event) => {
    const li = document.createElement('li');
    const title = document.createElement('span');
    title.textContent = `${event.emoji ?? ''} ${event.label ?? event.tool}`;
    const summary = document.createElement('p');
    summary.textContent = event.break_summary || event.message || '';
    const time = document.createElement('time');
    time.dateTime = event.timestamp;
    time.textContent = formatRelative(event.timestamp);

    const metrics = document.createElement('p');
    metrics.className = 'event-metrics';
    metrics.textContent = `Stress ${event.stress_level ?? '-'} / Boss ${event.boss_alert_level ?? '-'}`;

    li.appendChild(title);
    li.appendChild(summary);
    li.appendChild(metrics);
    li.appendChild(time);
    fragment.appendChild(li);
  });
  eventsList.appendChild(fragment);
}

function formatRelative(isoString) {
  if (!isoString) return '-';
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
}

loadActions().then(refreshEvents);
setInterval(refreshEvents, 6000);
