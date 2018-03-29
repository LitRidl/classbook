const { ipcRenderer, clipboard } = require('electron')

const printPDFBtn = document.getElementById('button-pdf')

printPDFBtn.addEventListener('click', (event) => {
  ipcRenderer.send('print-to-pdf')
})

const siteBtn = document.getElementById('copy-site')
const emailBtn = document.getElementById('copy-email')
const telegramBtn = document.getElementById('copy-telegram')

siteBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-site').innerText)
})

emailBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-email').innerText)
})

telegramBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-telegram').innerText)
})
