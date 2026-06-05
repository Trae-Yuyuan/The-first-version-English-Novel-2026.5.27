/**
 * Zustand store for the Debater page.
 * Persisted to localStorage — settings, sessions, messages.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

const MAX_SESSIONS = 30;
const MAX_MESSAGES = 100;

export const VoiceState = {
  IDLE: "idle",
  RECORDING: "recording",
  TRANSCRIBING: "transcribing",
  THINKING: "thinking",
  SPEAKING: "speaking",
  ERROR: "error",
};

const useDebaterStore = create(
  persist(
    (set, get) => ({
      // ── Settings ──────────────────────────────────────────
      settings: {
        apiKey: "",
        debateBotId: "",
        discussBotId: "",
        cozeApiUrl: "",
      },

      setSettings: (settings) =>
        set((state) => ({ settings: { ...state.settings, ...settings } })),

      // ── Sessions ──────────────────────────────────────────
      sessions: {},
      currentSessionId: null,

      setCurrentSessionId: (id) => set({ currentSessionId: id }),

      createSession: () => {
        const id = crypto.randomUUID();
        const now = Date.now();
        set((state) => {
          const sessions = { ...state.sessions };
          sessions[id] = {
            mode: "debate",
            messages: [],
            createdAt: now,
            updatedAt: now,
          };
          // Enforce max sessions
          const ids = Object.keys(sessions);
          if (ids.length > MAX_SESSIONS) {
            const oldest = ids.sort(
              (a, b) => sessions[a].createdAt - sessions[b].createdAt
            )[0];
            delete sessions[oldest];
          }
          return { sessions, currentSessionId: id };
        });
        return id;
      },

      deleteSession: (id) =>
        set((state) => {
          const sessions = { ...state.sessions };
          delete sessions[id];
          return {
            sessions,
            currentSessionId:
              state.currentSessionId === id ? null : state.currentSessionId,
          };
        }),

      // ── Messages ──────────────────────────────────────────
      addMessage: (sessionId, role, content, audioUrl = null) =>
        set((state) => {
          if (!sessionId) return state;
          const sessions = { ...state.sessions };
          let session = sessions[sessionId];
          // Auto-create session if it doesn't exist (belt-and-suspenders)
          if (!session) {
            const now = Date.now();
            session = {
              mode: state.mode || "debate",
              messages: [],
              createdAt: now,
              updatedAt: now,
            };
          }
          const messages = [
            ...session.messages,
            {
              role,
              content,
              audioUrl,
              timestamp: Date.now(),
            },
          ].slice(-MAX_MESSAGES);
          sessions[sessionId] = {
            ...session,
            messages,
            updatedAt: Date.now(),
          };
          // Also set currentSessionId if not set
          const currentSessionId =
            state.currentSessionId || sessionId;
          return { sessions, currentSessionId };
        }),

      // ── Mode ──────────────────────────────────────────────
      mode: "debate",

      setMode: (mode) => set({ mode }),

      // ── Voice State ───────────────────────────────────────
      voiceState: VoiceState.IDLE,

      setVoiceState: (voiceState) => set({ voiceState }),

      // ── Derived helpers ───────────────────────────────────
      getBotId: () => {
        const { settings, mode } = get();
        return mode === "debate"
          ? settings.debateBotId
          : settings.discussBotId;
      },

      getCurrentSession: () => {
        const { sessions, currentSessionId } = get();
        return currentSessionId ? sessions[currentSessionId] : null;
      },
    }),
    {
      name: "debater-store",
      version: 1,
      // Only persist data — never serialize functions (they cause JSON errors)
      partialize: (state) => ({
        settings: state.settings,
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        mode: state.mode,
        voiceState: state.voiceState,
      }),
      // Safe storage wrapper: catches quota / access errors
      storage: {
        getItem: (name) => {
          try {
            return localStorage.getItem(name);
          } catch {
            return null;
          }
        },
        setItem: (name, value) => {
          try {
            localStorage.setItem(name, value);
          } catch {
            // quota exceeded or private browsing — silently ignore
          }
        },
        removeItem: (name) => {
          try {
            localStorage.removeItem(name);
          } catch {
            // ignore
          }
        },
      },
    }
  )
);

export default useDebaterStore;
