const path = require('path')
const glob = require('glob')
const fs = require('fs')
const os = require('os')
const autoUpdater = require('./auto-updater')
const { app, BrowserWindow, ipcMain, shell, dialog } = require('electron')
const settings = require('electron-settings')

const debug = /--debug/.test(process.argv[2])
const enableDevTools = true

app.setName('Сборник задач по финансовой грамотности в информатике')

let mainWindow = null
let splash = null

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
      webPreferences: {
        devTools: enableDevTools,
      },
      show: false,
    }

    if (process.platform === 'linux') {
      windowOptions.icon = path.join(__dirname, '/assets/img/finformatika.png')
    }

    mainWindow = new BrowserWindow(windowOptions)
    mainWindow.setMenu(null)
    if (!enableDevTools) {
      mainWindow.webContents.on("devtools-opened", () => { mainWindow.webContents.closeDevTools(); });
    }
    mainWindow.loadURL(path.join('file://', __dirname, '/index.html'))

    splash = new BrowserWindow({ width: 400, height: 540, transparent: true, frame: false, alwaysOnTop: true });
    splash.loadURL(`file://${__dirname}/assets/img/loading.svg`);

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
    const pdfPath = path.join(os.tmpdir(), 'fingramotnost_print.pdf');
    // const win = BrowserWindow.fromWebContents(event.sender);
    mainWindow.webContents.printToPDF({ marginsType: 0, pageSize: 'A4', landscape: false, printSelectionOnly: false }, (error, data) => {
      if (error) throw error;
      fs.writeFile(pdfPath, data, (error) => {
        if (error) throw error;
        shell.openExternal(`file://${pdfPath}`);
      });
    });
  });

  ipcMain.on('save-dialog', (event, url) => {
    const srcPath = path.join(__dirname, url);
    const saveFile = (filename, data) => {
      fs.writeFile(filename, data, (error) => {
        if (error) {
          dialog.showErrorBox(
              'Ошибка при сохранении',
              `Детализация ошибки: ${error.message}`,
          );
        }
        shell.showItemInFolder(filename);
      });
    };
    const options = {
      title: 'Сохранить файл задачи',
      defaultPath: path.basename(srcPath),
      filters: [
        { name: 'Таблицы', extensions: ['xlsx'] },
        { name: 'Текстовые файлы', extensions: ['txt'] },
        { name: 'Все файлы', extensions: ['*'] },
      ],
    };
    dialog.showSaveDialog(options, (filename) => {
      if (filename === undefined) {
        return;
      }
      event.sender.send('saved-file', filename);
      fs.readFile(srcPath, (err, data) => {
        saveFile(filename, data);
      });
    });
  });
  

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


switch (process.argv[1]) {
  case '--squirrel-install':
    settings.deleteAll();
    autoUpdater.createShortcut(() => { app.quit() })
    break
  case '--squirrel-uninstall':
    settings.deleteAll();
    autoUpdater.removeShortcut(() => { app.quit() })
    break
  case '--squirrel-obsolete':
  case '--squirrel-updated':
    settings.deleteAll();
    autoUpdater.removeShortcut(() => { autoUpdater.createShortcut(() => { app.quit() }) })
    break
  default:
    initialize()
}
