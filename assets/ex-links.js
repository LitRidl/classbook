const shell = require('electron').shell;
const { ipcRenderer } = require('electron');

const links = document.querySelectorAll('a[href]');

Array.prototype.forEach.call(links, (link) => {
  const url = link.getAttribute('href');
  if (url.indexOf('http') === 0) {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      shell.openExternal(url);
    });
  }
  if (url.indexOf('assets/finformatika.ru/attachments') >= 0 || url.indexOf('assets/files/excel') >= 0) {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      ipcRenderer.send('save-dialog', url);
    });
  }
});

