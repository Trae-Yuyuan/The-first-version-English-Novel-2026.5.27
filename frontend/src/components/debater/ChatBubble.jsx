/**
 * ChatBubble — renders a single message.
 * - User: right-aligned, dark green background
 * - AI:   left-aligned, dark purple background, typing effect on latest
 */
import TypingText from "./TypingText";

export default function ChatBubble({ message, isTyping }) {
  const isUser = message.role === "user";

  return (
    <div className={`debater-bubble ${isUser ? "debater-bubble--user" : ""}`}>
      <div className="debater-bubble-avatar">
        {isUser ? "👤" : "🤖"}
      </div>
      <div
        className={`debater-bubble-content ${isUser ? "is-user" : "is-ai"}`}
      >
        {isTyping ? (
          <TypingText text={message.content} speed={25} />
        ) : (
          <p>{message.content}</p>
        )}
        {message.audioUrl && (
          <button
            className="nes-btn is-primary debater-audio-btn"
            onClick={() => new Audio(message.audioUrl).play()}
            title="Play voice response"
          >
            🔊 Play
          </button>
        )}
      </div>
    </div>
  );
}
