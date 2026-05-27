const { app, BrowserWindow } = require('electron')

function createWindow() {

  const win = new BrowserWindow({
    width: 1400,
    height: 900
  })

  // 打开 React 页面
  win.loadURL('http://localhost:5173')
}

app.whenReady().then(() => {
  createWindow()
})