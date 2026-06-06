import { useEffect, useCallback } from "react";
import ApiKeyInput from "../components/ApiKeyInput";
import NovelInput from "../components/NovelInput";
import VocabInput from "../components/VocabInput";
import OutputDisplay from "../components/OutputDisplay";
import { postTranslate } from "../api";
import useNovelStore from "../store/novelStore";

export default function EnglishNovel() {
  // ── Persisted state (Zustand) — survives page navigation ────
  const apiKey = useNovelStore((s) => s.apiKey);
  const novelText = useNovelStore((s) => s.novelText);
  const vocabText = useNovelStore((s) => s.vocabText);
  const novelReady = useNovelStore((s) => s.novelReady);
  const vocabReady = useNovelStore((s) => s.vocabReady);
  const result = useNovelStore((s) => s.result);
  const loading = useNovelStore((s) => s.loading);
  const error = useNovelStore((s) => s.error);

  const setApiKey = useNovelStore((s) => s.setApiKey);
  const setNovelText = useNovelStore((s) => s.setNovelText);
  const setVocabText = useNovelStore((s) => s.setVocabText);
  const setNovelReady = useNovelStore((s) => s.setNovelReady);
  const setVocabReady = useNovelStore((s) => s.setVocabReady);
  const setResult = useNovelStore((s) => s.setResult);
  const setLoading = useNovelStore((s) => s.setLoading);
  const setError = useNovelStore((s) => s.setError);

  const doTranslate = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await postTranslate(apiKey, novelText, vocabText);
      setResult(data);
      setNovelReady(false);
      setVocabReady(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiKey, novelText, vocabText]);

  useEffect(() => {
    if (novelReady && vocabReady && apiKey && novelText) {
      doTranslate();
    }
  }, [novelReady, vocabReady]);

  return (
    <div className="page-content">
      <header>
        <h1>AI Novel Translator</h1>
        <p>CET-4/6 Exam Prep x Interest Reading</p>
      </header>

      <main className="novel-main">
        {/* Window 1 — API Key + Novel Upload */}
        <div className="window window-col">
          <h3 className="window-title">Step 1 — Upload Novel</h3>
          <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
          <NovelInput
            novelText={novelText}
            setNovelText={setNovelText}
            ready={novelReady}
            setReady={setNovelReady}
          />
        </div>

        {/* Window 2 — Vocabulary Upload */}
        <div className="window window-col">
          <VocabInput
            vocabText={vocabText}
            setVocabText={setVocabText}
            ready={vocabReady}
            setReady={setVocabReady}
          />
        </div>

        {/* Window 3 — Output */}
        <div className="window window-col">
          <OutputDisplay result={result} loading={loading} error={error} />
        </div>
      </main>
    </div>
  );
}
