/**
 * Zustand store for the EnglishNovel (AI Novel Translator) page.
 * Persisted to localStorage — so text and results survive page navigation
 * and browser refresh.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

const useNovelStore = create(
  persist(
    (set) => ({
      // ── Form fields ─────────────────────────────────────────
      apiKey: "",
      novelText: "",
      vocabText: "",

      // ── UI state ────────────────────────────────────────────
      novelReady: false,
      vocabReady: false,
      result: null,
      loading: false,
      error: null,

      // ── Actions ─────────────────────────────────────────────
      setApiKey: (apiKey) => set({ apiKey }),
      setNovelText: (novelText) => set({ novelText }),
      setVocabText: (vocabText) => set({ vocabText }),
      setNovelReady: (ready) => set({ novelReady: ready }),
      setVocabReady: (ready) => set({ vocabReady: ready }),
      setResult: (result) => set({ result, loading: false }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error, loading: false }),
      clearResult: () => set({ result: null, error: null }),
    }),
    {
      name: "novel-store",
      version: 1,
      // Only persist the data/form fields — not transient UI state
      partialize: (state) => ({
        apiKey: state.apiKey,
        novelText: state.novelText,
        vocabText: state.vocabText,
        result: state.result,
      }),
    }
  )
);

export default useNovelStore;
