const settings = require('electron-settings');

document.body.addEventListener('click', (event) => {
  if (event.target.dataset.section) {
    handleSectionTrigger(event);
  }
});

const buttonPdf = document.getElementById('button-pdf');
const buttonReport = document.getElementById('button-report');
const buttonSearch = document.getElementById('button-search');
const spinner = document.getElementById('spinner');
const searchWindow = document.getElementsByClassName('electron-in-page-search-window')[0];

function handleSectionTrigger(event) {
  hideAllSectionsAndDeselectButtons();

  // Highlight clicked button and show view
  event.target.classList.add('is-selected');

  // Display the current section
  const sectionId = `${event.target.dataset.section}-section`;
  document.getElementById(sectionId).classList.add('is-shown');

  if (sectionId === 'questions-section') {
    buttonPdf.style.display = '';
    buttonReport.style.display = '';
    buttonSearch.style.display = '';
  } else if (sectionId === 'usermanual-section' || sectionId === 'textbook-section' || sectionId === 'glossary-section') {
    buttonPdf.style.display = '';
    buttonSearch.style.display = 'none';
    buttonReport.style.display = 'none';
    spinner.style.display = 'none';
    if (window.inPageSearch) {
      window.inPageSearch.closeSearchWindow();
    }
  } else {
    buttonPdf.style.display = 'none';
    buttonSearch.style.display = 'none';
    buttonReport.style.display = 'none';
    spinner.style.display = 'none';
    if (window.inPageSearch) {
      window.inPageSearch.closeSearchWindow();
    }
  }

  // Save currently active button in localStorage
  const buttonId = event.target.getAttribute('id');
  settings.set('activeSectionButtonId', buttonId);
}

function activateDefaultSection() {
  document.getElementById('button-textbook').click();
}

function showMainContent() {
  document.querySelector('.js-nav').classList.add('is-shown');
  document.querySelector('.js-content').classList.add('is-shown');
}


function hideAllSectionsAndDeselectButtons() {
  const sections = document.querySelectorAll('.js-section.is-shown');
  Array.prototype.forEach.call(sections, (section) => {
    section.classList.remove('is-shown');
  });

  const buttons = document.querySelectorAll('.nav-button.is-selected');
  Array.prototype.forEach.call(buttons, (button) => {
    button.classList.remove('is-selected');
  });
}


// Default to the view that was active the last time the app was open
const sectionBtnId = settings.get('activeSectionButtonId');

if (sectionBtnId) {
  const sectionBtn = document.getElementById(sectionBtnId);
  if (sectionBtn) {
    sectionBtn.click();
  } else {
    activateDefaultSection(); // TODO: check stability
  }
} else {
  activateDefaultSection();
}
