/**
 * ChatInput — bottom bar with:
 * - Mode toggle (Debate / Discuss)
 * - Voice toggle (Text / Voice)
 * - Text input or VoiceButton
 * - Send button
 */
import { useState, useRef } from "react";
import VoiceButton from "./VoiceButton";

export default function ChatInput({
  mode,
  onToggleMode,
  voiceMode,
  onToggleVoice,
  onSend,
  disabled,
}) {
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
    inputRef.current?.focus();
  };

  const handleVoiceResult = (transcript) => {
    onSend(transcript);
  };

  const placeholder =
    mode === "debate"
      ? "Make your argument..."
      : "Share your thoughts...";

  return (
    <div className="debater-input-bar">
      {/* Row 1: toggles */}
      <div className="debater-toggles">
        <label className="debater-toggle">
          <span>⚔ Debate</span>
          <input
            type="checkbox"
            className="nes-toggle"
            checked={mode === "discuss"}
            onChange={(e) =>
              onToggleMode(e.target.checked ? "discuss" : "debate")
            }
          />
          <span>💬 Discuss</span>
        </label>

        <label className="debater-toggle">
          <span>📝 Text</span>
          <input
            type="checkbox"
            className="nes-toggle"
            checked={voiceMode}
            onChange={(e) => onToggleVoice(e.target.checked)}
          />
          <span>🎤 Voice</span>
        </label>
      </div>

      {/* Row 2: input area */}
      <div className="debater-input-row">
        {voiceMode ? (
          <VoiceButton disabled={disabled} onResult={handleVoiceResult} />
        ) : (
          <>
            <input
              ref={inputRef}
              type="text"
              className="nes-input debater-text-input"
              placeholder={placeholder}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={disabled}
            />
            <button
              className="nes-btn is-primary debater-send-btn"
              onClick={handleSend}
              disabled={disabled || !text.trim()}
            >
              Send
            </button>
          </>
        )}
      </div>
    </div>
  );
}
