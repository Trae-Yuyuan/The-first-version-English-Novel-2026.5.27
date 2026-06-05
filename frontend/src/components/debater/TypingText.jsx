/**
 * TypingText — character-by-character reveal effect for AI messages.
 */
import { useState, useEffect, useRef } from "react";

export default function TypingText({ text, speed = 25, onComplete }) {
  const [displayed, setDisplayed] = useState("");
  const indexRef = useRef(0);

  useEffect(() => {
    indexRef.current = 0;
    setDisplayed("");

    if (!text) {
      onComplete?.();
      return;
    }

    const interval = setInterval(() => {
      indexRef.current += 1;
      setDisplayed(text.slice(0, indexRef.current));
      if (indexRef.current >= text.length) {
        clearInterval(interval);
        onComplete?.();
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <p className="debater-typing">
      {displayed}
      {displayed.length < (text?.length || 0) && (
        <span className="debater-cursor">|</span>
      )}
    </p>
  );
}
