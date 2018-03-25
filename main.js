const path = require('path')
const glob = require('glob')
const fs = require('fs')
const os = require('os')
const { app, BrowserWindow, ipcMain, shell } = require('electron')

const debug = /--debug/.test(process.argv[2])

app.setName('Сборник задач по финансовой грамотности в информатике')

let mainWindow = null

function initialize() {
  const shouldQuit = makeSingleInstance()
  if (shouldQuit) return app.quit()

  function createWindow() {
    const windowOptions = {
      width: 1920 * 0.7,
      minWidth: 1080,
      height: 1030,
      title: app.getName(),
      plugins: true,
      show: false,
    }

    if (process.platform === 'linux') {
      windowOptions.icon = path.join(__dirname, '/assets/img/finformatika.png')
    }

    mainWindow = new BrowserWindow(windowOptions)
    mainWindow.setMenu(null)
    mainWindow.loadURL(path.join('file://', __dirname, '/index.html'))

    splash = new BrowserWindow({ width: 1400, height: 1400, transparent: true, frame: false, alwaysOnTop: true });
    splash.loadURL(`file://${__dirname}/assets/img/cs.svg`);

    mainWindow.once('ready-to-show', () => {
      splash.destroy()
      mainWindow.show()
    })

    // Launch fullscreen with DevTools open, usage: npm run debug
    if (debug) {
      mainWindow.webContents.openDevTools()
      mainWindow.maximize()
      require('devtron').install()
    }

    mainWindow.on('closed', () => {
      mainWindow = null
    })
  }

  ipcMain.on('print-to-pdf', (event) => {
    const pdfPath = path.join(os.tmpdir(), 'fingramotnost_print.pdf')
    const win = BrowserWindow.fromWebContents(event.sender)
    win.webContents.printToPDF({}, (error, data) => {
      if (error) throw error
      fs.writeFile(pdfPath, data, (error) => {
        if (error) throw error
        shell.openExternal(`file://${pdfPath}`)
      })
    })
  })

  app.on('ready', () => {
    createWindow()
  })

  app.on('window-all-closed', () => {
    // if (process.platform !== 'darwin') {
    //   app.quit()
    // }
    app.quit()
  })

  app.on('activate', () => {
    if (mainWindow === null) {
      createWindow()
    }
  })
}

// Make this app a single instance app.
//
// The main window will be restored and focused instead of a second window
// opened when a person attempts to launch a second instance.
//
// Returns true if the current version of the app should quit instead of
// launching.
function makeSingleInstance() {
  if (process.mas) return false

  return app.makeSingleInstance(() => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}

// Handle Squirrel on Windows startup events
switch (process.argv[1]) {
  case '--squirrel-install':
    break
  case '--squirrel-uninstall':
    break
  case '--squirrel-obsolete':
  case '--squirrel-updated':
    app.quit()
    break
  default:
    initialize()
}
