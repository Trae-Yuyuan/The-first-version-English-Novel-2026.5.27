/**
 * usePageState — isolated per-page message state with localStorage persistence.
 *
 * Each page (debate / discuss) manages its own messages independently.
 * Switching pages preserves each page's messages.  Closing and reopening
 * the browser restores the last session's messages from localStorage.
 *
 * Usage:
 *   const { messages, sendMessage, clearMessages } = usePageState('debate');
 */

import { useState, useCallback, useEffect, useRef } from "react";

const STORAGE_PREFIX = "msgs";

function storageKey(pageKey, sessionId) {
  return `${STORAGE_PREFIX}_${pageKey}_${sessionId}`;
}

function loadFromStorage(pageKey, sessionId) {
  try {
    const raw = localStorage.getItem(storageKey(pageKey, sessionId));
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch {
    // corrupted — ignore
  }
  return [];
}

function saveToStorage(pageKey, sessionId, messages) {
  try {
    if (messages.length === 0) {
      localStorage.removeItem(storageKey(pageKey, sessionId));
    } else {
      // Keep only the last 100 messages to stay under quota
      const trimmed = messages.slice(-100);
      localStorage.setItem(
        storageKey(pageKey, sessionId),
        JSON.stringify(trimmed)
      );
    }
  } catch {
    // quota exceeded — oldest messages are already trimmed above
  }
}

export default function usePageState(pageKey) {
  // Track the current sessionId in a ref so we re-load when it changes
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const loadedRef = useRef(null);

  // When sessionId changes, load messages for that session
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    const key = storageKey(pageKey, sessionId);
    if (loadedRef.current === key) return; // already loaded
    loadedRef.current = key;
    setMessages(loadFromStorage(pageKey, sessionId));
  }, [pageKey, sessionId]);

  // Persist on every change
  useEffect(() => {
    if (sessionId && loadedRef.current) {
      saveToStorage(pageKey, sessionId, messages);
    }
  }, [pageKey, sessionId, messages]);

  const addMessage = useCallback((role, content, audioUrl = null) => {
    setMessages((prev) => [
      ...prev,
      {
        role,
        content,
        audioUrl,
        timestamp: Date.now(),
      },
    ]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sessionId,
    setSessionId,
    addMessage,
    clearMessages,
  };
}
