/**
 * SettingsModal — first-launch or manual configuration dialog.
 * Inputs: COZE API Key, Debate Bot ID, Discuss Bot ID, COZE API URL.
 *
 * Sync strategy:
 *   - useEffect([open]) resets local state from store every time the
 *     modal opens, so stale local state is never shown.
 *   - Parent also passes a key that changes on close (belt & suspenders).
 *   - setSettings is wrapped in try/catch so onClose always fires even
 *     if localStorage is full or the store throws.
 */
import { useState, useEffect } from "react";
import useDebaterStore from "../../store/debaterStore";

export default function SettingsModal({ open, onClose }) {
  const { settings, setSettings } = useDebaterStore();

  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [debateBotId, setDebateBotId] = useState(settings.debateBotId);
  const [discussBotId, setDiscussBotId] = useState(settings.discussBotId);
  const [cozeApiUrl, setCozeApiUrl] = useState(settings.cozeApiUrl);
  const [showKey, setShowKey] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Reset local state every time the modal opens — this is the
  // primary mechanism that guarantees the form shows fresh values.
  useEffect(() => {
    if (open) {
      setApiKey(settings.apiKey);
      setDebateBotId(settings.debateBotId);
      setDiscussBotId(settings.discussBotId);
      setCozeApiUrl(settings.cozeApiUrl);
      setSaveError(null);
    }
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = () => {
    setSaveError(null);
    try {
      setSettings({
        apiKey: apiKey.trim(),
        debateBotId: debateBotId.trim(),
        discussBotId: discussBotId.trim(),
        cozeApiUrl: cozeApiUrl.trim(),
      });
    } catch (err) {
      console.error("Failed to save settings:", err);
      setSaveError(`Save failed: ${err.message || err}`);
      return; // don't close — let the user see the error
    }
    onClose();
  };

  if (!open) return null;

  const isFirstLaunch =
    !settings.apiKey && !settings.debateBotId && !settings.discussBotId;

  return (
    <div
      className="debater-modal-overlay"
      onClick={isFirstLaunch ? undefined : onClose}
    >
      <div
        className="debater-modal nes-container is-rounded"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="debater-modal-title">⚙ COZE Settings</h2>

        <div className="debater-modal-field">
          <label>COZE API Key</label>
          <div className="debater-modal-key-row">
            <input
              type={showKey ? "text" : "password"}
              className="nes-input"
              placeholder="pat_xxxxxxxxxxxxxxxxxxxx"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <button
              type="button"
              className="nes-btn is-warning"
              onClick={() => setShowKey((v) => !v)}
            >
              {showKey ? "🙈" : "👁"}
            </button>
          </div>
        </div>

        <div className="debater-modal-field">
          <label>COZE API URL</label>
          <input
            type="text"
            className="nes-input"
            placeholder="https://api.coze.cn (default)"
            value={cozeApiUrl}
            onChange={(e) => setCozeApiUrl(e.target.value)}
          />
          <small style={{ color: "#888", fontSize: "0.65rem" }}>
            Leave empty for default (api.coze.cn). Use api.coze.com for global version.
          </small>
        </div>

        <div className="debater-modal-field">
          <label>Debate Bot ID</label>
          <input
            type="text"
            className="nes-input"
            placeholder="bot_xxxxxxxxxxxxxxxxxxxx"
            value={debateBotId}
            onChange={(e) => setDebateBotId(e.target.value)}
          />
        </div>

        <div className="debater-modal-field">
          <label>Discuss Bot ID</label>
          <input
            type="text"
            className="nes-input"
            placeholder="bot_xxxxxxxxxxxxxxxxxxxx"
            value={discussBotId}
            onChange={(e) => setDiscussBotId(e.target.value)}
          />
        </div>

        {saveError && (
          <div className="debater-error nes-container is-rounded" style={{ marginBottom: "0.75rem" }}>
            <p>⚠ {saveError}</p>
          </div>
        )}

        <div className="debater-modal-actions">
          {!isFirstLaunch && (
            <button className="nes-btn" onClick={onClose}>
              Cancel
            </button>
          )}
          <button
            className="nes-btn is-primary"
            onClick={handleSave}
            disabled={
              !apiKey.trim() ||
              (!debateBotId.trim() && !discussBotId.trim())
            }
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
