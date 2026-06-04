import { useState, useEffect, useCallback } from "react";
import ApiKeyInput from "./components/ApiKeyInput";
import NovelInput from "./components/NovelInput";
import VocabInput from "./components/VocabInput";
import OutputDisplay from "./components/OutputDisplay";
import { postTranslate } from "./api";
import "./App.css";

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [novelText, setNovelText] = useState("");
  const [vocabText, setVocabText] = useState("");
  const [novelReady, setNovelReady] = useState(false);
  const [vocabReady, setVocabReady] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const doTranslate = useCallback(async () => {
    setError(null);
    setLoading(true);
    setResult(null);
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
    <div className="app-container">
      <header>
        <h1>📖 AI Novel Translator</h1>
        <p>CET-4/6 Exam Prep × Interest Reading</p>
      </header>

      <main>
        {/* Window 1 — API Key + Novel Upload */}
        <div className="window window-col">
          <h3 className="window-title">📖 Step 1 — Upload Novel</h3>
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
