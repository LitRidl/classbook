"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const search_button = document.querySelector('.inpage-search-button');
const matches = document.querySelector('.inpage-search-matches');
const back_button = document.querySelector('.inpage-search-back');
const forward_button = document.querySelector('.inpage-search-forward');
// const close_button = document.querySelector('.inpage-search-close');
const search_input = document.querySelector('.inpage-search-input');
const search_clear_button = document.getElementById('button-search-clear');
let in_composition = false;
if (search_button !== null) {
    search_button.addEventListener('click', () => {
        const input = search_input.value;
        if (input === '') {
            return;
        }
        electron_1.ipcRenderer.sendToHost('electron-in-page-search:query', input);
    });
}
if (back_button !== null) {
    back_button.addEventListener('click', () => {
        electron_1.ipcRenderer.sendToHost('electron-in-page-search:back', search_input.value);
    });
}
if (forward_button !== null) {
    forward_button.addEventListener('click', () => {
        electron_1.ipcRenderer.sendToHost('electron-in-page-search:forward', search_input.value);
    });
}
search_clear_button.addEventListener('click', () => {
    electron_1.ipcRenderer.sendToHost('electron-in-page-search:close');
});
search_input.addEventListener('keyup', e => {
    if (in_composition) {
        console.log('Keydown skipped!!')
        return;
    }
    if (search_input.value === '') {
        search_clear_button.style.display = '';
    }
    switch (e.code) {
        case 'Enter':
        case 'NumpadEnter':
            if (search_input.value === '') {
                electron_1.ipcRenderer.sendToHost('electron-in-page-search:close');
            }
            if (e.shiftKey) {
                electron_1.ipcRenderer.sendToHost('electron-in-page-search:back', search_input.value);
            }
            else {
                electron_1.ipcRenderer.sendToHost('electron-in-page-search:query', search_input.value);
            }
            break;
        case 'Escape':
            electron_1.ipcRenderer.sendToHost('electron-in-page-search:close');
            break;
        case 'KeyG':
            if (e.ctrlKey) {
                electron_1.ipcRenderer.sendToHost('electron-in-page-search:close');
            }
            break;
        default:
            if (search_input.value != '') {
                search_clear_button.style.display = 'block';
            }
            return;
    }
});
search_input.addEventListener('compositionstart', () => {
    in_composition = true;
});
search_input.addEventListener('compositionend', () => {
    in_composition = false;
});
electron_1.ipcRenderer.on('electron-in-page-search:focus', () => {
    // console.log('Focus on input');
    // search_input.focus();
    window.setTimeout(function () {  search_input.focus();  }, 10); 
});
electron_1.ipcRenderer.on('electron-in-page-search:result', (_, nth, all) => {
    matches.innerText = `${nth}/${all}`;
    search_input.classList.toggle('inpage-search-input-noresults', all === 0);
});
electron_1.ipcRenderer.on('electron-in-page-search:close', () => {
    search_input.value = '';
    matches.innerText = '0/0';
    search_clear_button.style.display = '';
    window.setTimeout(function () {  search_input.focus();  }, 10); 
});
//# sourceMappingURL=search-window.js.map