window.addEventListener("submit", (e) => {
  console.log("BLOCKED SUBMIT")
  e.preventDefault()
  e.stopPropagation()
})

window.addEventListener("beforeunload", (e) => {
  console.log("PAGE RELOAD TRIGGERED")
})
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./index.css"
import 'nes.css/css/nes.min.css'
import '@fontsource/press-start-2p'
import './styles/layout.css'
import './styles/crt.css'
ReactDOM.createRoot(document.getElementById("root")).render(
  <App />
)
document.addEventListener("click", (e) => {
  console.log("CLICK TARGET:", e.target)
})