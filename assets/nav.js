const settings = require('electron-settings');

document.body.addEventListener('click', (event) => {
  if (event.target.dataset.section) {
    handleSectionTrigger(event);
  }
});

const textbook_ = document.getElementById('textbook-section');
const glossary_ = document.getElementById('glossary-section');
const questions_ = document.getElementById('questions-section');
const usermanual_ = document.getElementById('usermanual-section');

const buttonPdf = document.getElementById('button-pdf');
const buttonTop = document.getElementById('button-top');
const buttonReport = document.getElementById('button-report');
// const buttonSearch = document.getElementById('button-search');
const spinner = document.getElementById('spinner');
// const searchWindow = document.getElementsByClassName('electron-in-page-search-window')[0];

const fixButtonTopFor = (el) => {
  buttonTop.style.display = (el.scrollTop > 20)? 'block' : 'none';
};

const registerScrollButtonTop = (el) => {
  el.addEventListener('scroll', (event) => fixButtonTopFor(el));
};

registerScrollButtonTop(textbook_);
registerScrollButtonTop(glossary_);
registerScrollButtonTop(questions_);
registerScrollButtonTop(usermanual_);
registerScrollButtonTop(textbook_);

// When the user clicks on the button, scroll to the top of the document
buttonTop.addEventListener('click', (event) => {
  textbook_.scrollTop = 0;
  glossary_.scrollTop = 0;
  questions_.scrollTop = 0;
  usermanual_.scrollTop = 0;
});


function handleSectionTrigger(event) {
  hideAllSectionsAndDeselectButtons();

  // Highlight clicked button and show view
  event.target.classList.add('is-selected');

  // Display the current section
  const sectionId = `${event.target.dataset.section}-section`;
  document.getElementById(sectionId).classList.add('is-shown');

  if (sectionId === 'questions-section') {
    fixButtonTopFor(questions_);
    buttonTop.style.display = '';
    buttonPdf.style.display = '';
    buttonReport.style.display = '';
    // buttonSearch.style.display = '';
  } else if (sectionId === 'usermanual-section' || sectionId === 'textbook-section' || sectionId === 'glossary-section') {
    buttonPdf.style.display = '';
    // buttonSearch.style.display = 'none';
    buttonReport.style.display = 'none';
    spinner.style.display = 'none';
    // if (window.inPageSearch) {
    //   window.inPageSearch.closeSearchWindow();
    // }
    const tocbotOptions = {
      collapseDepth: 3,
      scrollSmooth: true,
      scrollSmoothDuration: 420,
      positionFixedSelector: null,
      positionFixedClass: 'is-position-fixed',
      orderedList: false,
      linkClass: 'nononono223235', //'toc-link',
      extraLinkClasses: '',
      activeLinkClass: 'nononono23423', //'is-active-link',
      listClass: 'toc-list',
      extraListClasses: '',
      listItemClass: 'toc-list-item',
    };
    if (sectionId === 'usermanual-section') { fixButtonTopFor(usermanual_); }
    else if (sectionId === 'textbook-section') {
      fixButtonTopFor(textbook_);
      tocbot.init(Object.assign(tocbotOptions, {
        tocSelector: '#toc-textbook',
        contentSelector: '#textbook-section',
        headingSelector: '.h1-good, h2',
      }));
    } else if (sectionId === 'glossary-section') {
      fixButtonTopFor(glossary_);
      tocbot.init(Object.assign(tocbotOptions, {
        tocbotOptions,
        tocSelector: '#toc-glossary',
        contentSelector: '#glossary-section',
        headingSelector: '.glossary-concept',
        listItemClass: 'toc-list-item-glossary',
        listClass: 'toc-list-glossary',
      }));
    }
  } else {
    buttonTop.style.display = '';
    buttonPdf.style.display = 'none';
    // buttonSearch.style.display = 'none';
    buttonReport.style.display = 'none';
    spinner.style.display = 'none';
    // if (window.inPageSearch) {
    //   window.inPageSearch.closeSearchWindow();
    // }
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

  tocbot.destroy();
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
