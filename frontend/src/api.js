/**
 * HTTP API service layer.
 * All communication with the Flask backend goes through here.
 */
const API_BASE = "/api";

export async function postTranslate(apiKey, novelText, vocabText) {
  const response = await fetch(`${API_BASE}/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      api_key: apiKey,
      novel_text: novelText,
      vocab_text: vocabText,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}: Request failed`);
  }

  return data;
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}

// ── Debater / COZE Chat ─────────────────────────────────────

export async function postChat({ api_key, bot_id, session_id, message, mode, api_url }) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      api_key,
      bot_id,
      session_id,
      message,
      mode,
      api_url,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}: Request failed`);
  }

  return data;
}

export async function getSessions() {
  const response = await fetch(`${API_BASE}/sessions`);
  return response.json();
}

export async function deleteSessionApi(id) {
  const response = await fetch(
    `${API_BASE}/sessions/${encodeURIComponent(id)}`,
    { method: "DELETE" }
  );
  return response.json();
}

// ── Backend Config (config.json on disk) ──────────────────────

export async function getBackendConfig() {
  const response = await fetch(`${API_BASE}/config`);
  if (!response.ok) {
    throw new Error(`Config fetch failed: HTTP ${response.status}`);
  }
  return response.json();
}

export async function saveBackendConfig(updates) {
  const response = await fetch(`${API_BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `Config save failed: HTTP ${response.status}`);
  }
  return response.json();
}

// ── Graceful shutdown (EXE mode) ──────────────────────────────

export async function requestShutdown() {
  try {
    await fetch(`${API_BASE}/shutdown`, { method: "POST" });
  } catch {
    // Server already shutting down — ignore
  }
}
