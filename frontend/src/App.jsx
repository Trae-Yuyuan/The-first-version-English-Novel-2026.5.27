import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import EnglishNovel from "./pages/EnglishNovel";
import Debater from "./pages/Debater";
import Minecrafter from "./pages/Minecrafter";
import "./App.css";

export default function App() {
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
