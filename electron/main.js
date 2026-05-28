const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow() {

  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  // 🚨 强制 dev 模式
  const isDev = !app.isPackaged

  if (isDev) {
    console.log("DEV MODE → loading Vite")
    win.loadURL('http://localhost:5173')
  } else {
    console.log("PROD MODE → loading dist")
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)