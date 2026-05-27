import { useState } from 'react'

import WindowPanel from '../components/WindowPanel'
import DropZone from '../components/DropZone'
import PixelButton from '../components/PixelButton'

// 🐱 GIF
import computerGif from '../assets/computer.gif'

function MainUI() {

  const [novelFile, setNovelFile] = useState(null)
  const [vocabFile, setVocabFile] = useState(null)

  const [apiKey, setApiKey] = useState("")
  const [showKey, setShowKey] = useState(false)

  const [stage, setStage] = useState("idle")

  const [logs, setLogs] = useState([
    '> system initialized...',
    '> waiting for input...',
    '> please enter API key'
  ])

  const [typedOutput, setTypedOutput] = useState("")
  const [tasks, setTasks] = useState([])

  // ✅ 下载链接
  const [downloadUrl, setDownloadUrl] = useState("")

  // ✅ vocab词表
  const [vocabWords, setVocabWords] = useState([])

  let buttonText = "RUN AI"

  if (!apiKey) buttonText = "ENTER API KEY"
  else if (stage === "processing") buttonText = "PROCESSING..."
  else if (stage === "done") buttonText = "RUN AGAIN"

  const preventDefaults = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleNovelUpload = (file) => {

    setNovelFile(file)

    setLogs(prev => [
      ...prev,
      `> novel loaded: ${file.name}`
    ])
  }

  // ✅ 读取 vocab 文件内容
  const handleVocabUpload = async (file) => {

    setVocabFile(file)

    setLogs(prev => [
      ...prev,
      `> vocab loaded: ${file.name}`
    ])

    const text = await file.text()

    const words = text
      .split(/\r?\n/)
      .map(w => w.trim().toLowerCase())
      .filter(Boolean)

    setVocabWords(words)
  }

  // ✅ 高亮函数
  const renderHighlightedText = () => {

    const parts = typedOutput.split(/(\s+)/)

    return parts.map((part, index) => {

      const clean = part
        .replace(/[.,!?;:"]/g, "")
        .toLowerCase()

      const isHighlight =
        vocabWords.includes(clean)

      return (
        <span
          key={index}
          style={{
            color: isHighlight
              ? "#ffffff"
              : "#00ff00",

            fontWeight: isHighlight
              ? "bold"
              : "normal"
          }}
        >
          {part}
        </span>
      )
    })
  }

  const handleProcess = async () => {

    if (!apiKey || !novelFile || !vocabFile)
      return

    setStage("processing")
    setTypedOutput("")
    setDownloadUrl("")

    const formData = new FormData()

    formData.append("novel", novelFile)
    formData.append("vocab", vocabFile)
    formData.append("api_key", apiKey)

    const res = await fetch(
      "http://localhost:5000/process",
      {
        method: "POST",
        body: formData
      }
    )

    if (!res.body) {
      setStage("idle")
      return
    }

    const reader = res.body.getReader()

    const decoder =
      new TextDecoder("utf-8")

    let buffer = ""

    while (true) {

      const { value, done } =
        await reader.read()

      if (done) break

      buffer += decoder.decode(
        value,
        { stream: true }
      )

      const parts =
        buffer.split("\n\n")

      buffer = parts.pop()

      for (let p of parts) {

        if (!p.includes("data:"))
          continue

        const jsonStr =
          p.replace("data: ", "")

        let data

        try {
          data = JSON.parse(jsonStr)
        } catch {
          continue
        }

        // STREAM
        if (data.char) {

          setTypedOutput(prev =>
            prev + data.char
          )
        }

        // DONE
        if (data.done) {

          setStage("done")

          // ✅ 下载链接
          if (data.download_url) {

            setDownloadUrl(
              `http://localhost:5000${data.download_url}`
            )
          }
        }
      }
    }
  }

  return (

    <div
      className="app-container"

      onDragEnter={preventDefaults}
      onDragOver={preventDefaults}
      onDrop={preventDefaults}
    >

      <div
        style={{
          color: "#00ff00",
          marginBottom: "10px"
        }}
      >
        SYSTEM STATUS:
        {stage.toUpperCase()}
      </div>

      <div className="window-grid">

        {/* WINDOW 1 */}
        <WindowPanel title="INPUT CONTROL">

          <input
            type={
              showKey
                ? "text"
                : "password"
            }

            value={apiKey}

            onChange={(e) =>
              setApiKey(e.target.value)
            }
          />

          <button
            onClick={() =>
              setShowKey(v => !v)
            }
          >
            {
              showKey
                ? "HIDE KEY"
                : "SHOW KEY"
            }
          </button>

          <DropZone
            text={
              novelFile
                ? novelFile.name
                : "Drop Novel"
            }

            onFileDrop={
              handleNovelUpload
            }
          />

          <PixelButton
            text={buttonText}
            onClick={handleProcess}
          />

        </WindowPanel>

        {/* WINDOW 2 */}
        <WindowPanel title="VOCABULARY">

          <DropZone
            text={
              vocabFile
                ? vocabFile.name
                : "Drop Vocab"
            }

            onFileDrop={
              handleVocabUpload
            }
          />

          <PixelButton text="SYNC" />

          {/* GIF */}
          <div
            style={{
              marginTop: "10px",
              textAlign: "center"
            }}
          >

            <img
              src={computerGif}
              alt="computer gif"

              style={{
                width: "100%",
                maxWidth: "200px",
                height: "auto",
                imageRendering:
                  "pixelated"
              }}
            />

          </div>

        </WindowPanel>

        {/* WINDOW 3 */}
        <WindowPanel title="OUTPUT SYSTEM">

          <div className="fake-doc">

            {logs.map((l, i) => (
              <div key={i}>
                {l}
              </div>
            ))}

            {/* ✅ 高亮输出 */}
            <div
              style={{
                marginTop: "10px",
                color: "#00ff00"
              }}
            >
              {renderHighlightedText()}
            </div>

            <span className="cursor">
              █
            </span>

          </div>

          {/* ✅ DOWNLOAD */}
          {downloadUrl && (

            <div
              style={{
                marginTop: "15px"
              }}
            >

              <a
                href={downloadUrl}
                target="_blank"
                rel="noreferrer"

                style={{
                  color: "#ffffff",
                  border:
                    "1px solid #ffffff",

                  padding: "6px 10px",

                  textDecoration: "none",

                  display: "inline-block"
                }}
              >
                DOWNLOAD OUTPUT
              </a>

            </div>
          )}

          {/* HISTORY */}
          <div
            style={{
              marginTop: "15px",
              color: "#00ff00"
            }}
          >

            <h4>HISTORY</h4>

            {tasks.map(t => (

              <div
                key={t.id}

                style={{
                  fontSize: "12px"
                }}
              >
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