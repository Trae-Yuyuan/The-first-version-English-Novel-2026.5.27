/**
 * Highlight utility: inserts <span class="vocab-hl"> tags around
 * vocabulary words in the translated text based on backend position data.
 *
 * Uses reverse-order insertion to avoid position offset issues.
 */

/**
 * Convert highlights array to HTML string with highlighted spans.
 * @param {string} text - Clean translated text
 * @param {{word: string, start: number, end: number}[]} highlights
 * @returns {string} HTML string with <span> tags inserted
 */
export function applyHighlights(text, highlights) {
  if (!highlights || highlights.length === 0) {
    return escapeHtml(text);
  }

  // Sort by start position descending so inserts don't affect earlier positions
  const sorted = [...highlights].sort((a, b) => b.start - a.start);

  let result = escapeHtml(text);

  for (const { word, start, end } of sorted) {
    const before = result.slice(0, start);
    const highlighted = `<span class="vocab-hl">${result.slice(start, end)}</span>`;
    const after = result.slice(end);
    result = before + highlighted + after;
  }

  return result;
}

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (ch) => map[ch]);
}
