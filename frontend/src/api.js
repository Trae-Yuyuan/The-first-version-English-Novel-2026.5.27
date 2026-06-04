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
