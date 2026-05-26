import { useState } from 'react'

import WindowPanel from '../components/WindowPanel'
import DropZone from '../components/DropZone'
import PixelButton from '../components/PixelButton'

function MainUI() {

  // =========================
  // FILE STATE
  // =========================
  const [novelFile, setNovelFile] = useState(null)
  const [vocabFile, setVocabFile] = useState(null)

  // =========================
  // API KEY
  // =========================
  const [apiKey, setApiKey] = useState("")
  const [showKey, setShowKey] = useState(false)

  // =========================
  // SYSTEM STATE
  // =========================
  const [stage, setStage] = useState("idle")

  const [logs, setLogs] = useState([
    '> system initialized...',
    '> waiting for input...',
    '> please enter API key'
  ])

  const [typedOutput, setTypedOutput] = useState("")
  const [tasks, setTasks] = useState([])

  // =========================
  // BUTTON TEXT
  // =========================
  let buttonText = "RUN AI"
  if (!apiKey) buttonText = "ENTER API KEY"
  else if (stage === "processing") buttonText = "PROCESSING..."
  else if (stage === "done") buttonText = "RUN AGAIN"

  // =========================
  // EVENTS
  // =========================
  const preventDefaults = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleNovelUpload = (file) => {
    setNovelFile(file)
    setLogs(prev => [...prev, `> novel loaded: ${file.name}`])
  }

  const handleVocabUpload = (file) => {
    setVocabFile(file)
    setLogs(prev => [...prev, `> vocab loaded: ${file.name}`])
  }

  // =========================
  // STREAM PROCESS
  // =========================
  const handleProcess = async () => {

    if (!apiKey) {
      setLogs(prev => [...prev, "> error: missing API key"])
      return
    }

    if (!novelFile || !vocabFile) {
      setLogs(prev => [...prev, "> error: missing files"])
      return
    }

    setStage("processing")
    setTypedOutput("")

    setLogs(prev => [
      ...prev,
      "> uploading files...",
      "> AI processing started..."
    ])

    const formData = new FormData()
    formData.append("novel", novelFile)
    formData.append("vocab", vocabFile)
    formData.append("api_key", apiKey)

    const res = await fetch("http://localhost:5000/process", {
      method: "POST",
      body: formData
    })

    if (!res.body) {
      setLogs(prev => [...prev, "> error: no stream"])
      setStage("idle")
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder("utf-8")

    let buffer = ""

    while (true) {

      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const parts = buffer.split("\n\n")
      buffer = parts.pop()

      for (let p of parts) {

        if (!p.includes("data:")) continue

        const jsonStr = p.replace("data: ", "")
        let data

        try {
          data = JSON.parse(jsonStr)
        } catch {
          continue
        }

        if (data.char) {
          setTypedOutput(prev => prev + data.char)
        }

        if (data.done) {

          setStage("done")

          const task = {
            id: data.task_id,
            time: data.created_at,
            output: typedOutput
          }

          setTasks(prev => [task, ...prev])

          setLogs(prev => [
            ...prev,
            `> task saved: ${task.id}`
          ])
        }
      }
    }
  }

  // =========================
  // UI
  // =========================
  return (
    <div
      className="app-container"
      onDragEnter={preventDefaults}
      onDragOver={preventDefaults}
      onDrop={preventDefaults}
    >

      <div style={{ color: "#00ff00", marginBottom: "10px" }}>
        SYSTEM STATUS: {stage.toUpperCase()}
      </div>

      <div className="window-grid">

        {/* WINDOW 1 */}
        <WindowPanel title="INPUT CONTROL">

          <input
            type={showKey ? "text" : "password"}
            placeholder="Enter API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{
              width: "100%",
              padding: "6px",
              background: "black",
              color: "#00ff00",
              border: "1px solid #00ff00"
            }}
          />

          <button onClick={() => setShowKey(v => !v)}>
            {showKey ? "HIDE KEY" : "SHOW KEY"}
          </button>

          <DropZone
            text={novelFile ? novelFile.name : "Drop Novel"}
            onFileDrop={handleNovelUpload}
          />

          <PixelButton text={buttonText} onClick={handleProcess} />

        </WindowPanel>

        {/* WINDOW 2 */}
        <WindowPanel title="VOCABULARY">

          <DropZone
            text={vocabFile ? vocabFile.name : "Drop Vocab"}
            onFileDrop={handleVocabUpload}
          />

          <PixelButton text="SYNC" />

        </WindowPanel>

        {/* WINDOW 3 */}
        <WindowPanel title="OUTPUT SYSTEM">

          <div className="fake-doc">

            {logs.map((l, i) => (
              <div key={i}>{l}</div>
            ))}

            <div style={{ marginTop: "10px", color: "#00ff00" }}>
              {typedOutput}
            </div>

            <span className="cursor">█</span>

          </div>

          <div style={{ marginTop: "15px", color: "#00ff00" }}>
            <h4>HISTORY</h4>

            {tasks.map(t => (
              <div key={t.id} style={{ fontSize: "12px" }}>
                [{t.time}] {t.id}
              </div>
            ))}

          </div>

        </WindowPanel>

      </div>
    </div>
  )
}

export default MainUI