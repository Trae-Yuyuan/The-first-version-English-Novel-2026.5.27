import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import EnglishNovel from "./pages/EnglishNovel";
import Debater from "./pages/Debater";
import Minecrafter from "./pages/Minecrafter";
import { getBackendConfig, requestShutdown } from "./api";
import useDebaterStore from "./store/debaterStore";
import "./App.css";

export default function App() {
  const setSettings = useDebaterStore((s) => s.setSettings);

  // On mount: sync settings from backend config.json → Zustand store.
  // This ensures the EXE remembers API keys / Bot IDs across restarts.
  useEffect(() => {
    let cancelled = false;
    getBackendConfig()
      .then((cfg) => {
        if (cancelled) return;
        setSettings({
          apiKey: cfg.api_key || "",
          debateBotId: cfg.bot_id_debate || "",
          discussBotId: cfg.bot_id_discuss || "",
          cozeApiUrl: cfg.coze_api_url || "",
        });
      })
      .catch(() => {
        // Backend unreachable (dev mode?) — fall back to localStorage values
      });
    return () => { cancelled = true; };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // On tab/window close: tell the backend to shut down (EXE mode).
  // No-op if the backend is already gone or in dev mode.
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Use navigator.sendBeacon for reliable fire-and-forget
      navigator.sendBeacon("/api/shutdown");
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div className="main-area">
          <Routes>
            <Route path="/" element={<EnglishNovel />} />
            <Route path="/debater" element={<Debater />} />
            <Route path="/minecrafter" element={<Minecrafter />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
