// const {BrowserWindow} = require('electron').remote
// const path = require('path')

// const newWindowBtn = document.getElementById('new-window')

// newWindowBtn.addEventListener('click', (event) => {
//   const modalPath = path.join('file://', __dirname, '../../sections/windows/modal.html')
//   let win = new BrowserWindow({ width: 400, height: 320 })

//   win.on('close', () => { win = null })
//   win.loadURL(modalPath)
//   win.show()
// })

const { ipcRenderer } = require('electron')

const printPDFBtn = document.getElementById('button-pdf')

printPDFBtn.addEventListener('click', (event) => {
  ipcRenderer.send('print-to-pdf')
})
