const { ipcRenderer, clipboard } = require('electron')

const pdfBtn = document.getElementById('button-pdf');
pdfBtn.addEventListener('click', (event) => {
  ipcRenderer.send('print-to-pdf');
});

const siteBtn = document.getElementById('copy-site')
siteBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-site').innerText)
});

const emailBtn = document.getElementById('copy-email')
emailBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-email').innerText)
});


// Real logics

const storage = (key, value) => {
  if (value === undefined) {
    let item = localStorage.getItem(key);
    return (item === null)? null : JSON.parse(item);
  } else {
    localStorage.setItem(key, JSON.stringify(value));
    return value;
  }
};

const check_float = (answer, correct, tolerance) => {
  if (tolerance == 'null') {
    return +answer == +correct;
  }
  return (+answer >= +correct - +tolerance) && (+answer <= +correct + +tolerance);
};

const union = (setA, setB) => {
  var union = new Set(setA);
  for (const elem of setB) {
      union.add(elem);
  }
  return union;
};

function intersection(setA, setB) {
  var intersection = new Set();
  for (const elem of setB) {
      if (setA.has(elem)) {
          intersection.add(elem);
      }
  }
  return intersection;
}

const questionElements = document.getElementsByClassName('question');
const allQuestions = {};
const allQuestionsIdx = [];
for (let i = 0; i < questionElements.length; ++i) {
  const q = questionElements[i];
  allQuestions[+q.dataset.questionId] = q;
  allQuestionsIdx.push(+q.dataset.questionId);
}
allQuestionsIdx.sort();

const filtersBox = document.getElementById('filters-box');
const fieldsets = filtersBox.getElementsByTagName('fieldset');

const checkboxGroups = [];
for (let i = 0; i < fieldsets.length; i++) {
  const cbs = fieldsets[i].getElementsByTagName('input');
  checkboxGroups.push(cbs);
}

filtersBox.addEventListener('change', (event) => {
  let questions = new Set(allQuestionsIdx);

  for (let g = 0; g < checkboxGroups.length; ++g) {
    let questionsLocal = new Set();
    let hasChecked = false;
    for (let i = 0; i < checkboxGroups[g].length; ++i) {
      const cb = checkboxGroups[g][i];
      if (cb.checked) {
        hasChecked = true;
        questionsLocal = union(questionsLocal, new Set(questionsIndex[cb.name][cb.value]));
      }
    }
    if (hasChecked) {
      questions = intersection(questions, questionsLocal);
    }
  }

  for (let i = 0; i < questionElements.length; ++i) {
    const q = questionElements[i];
    if (questions.has(+q.dataset.questionId)) {
      q.style.display = '';
    } else {
      q.style.display = 'none';
    }
  }
  event.stopPropagation();
});

const modifySubmits = (questionId, firstTime, lastOk) => {
  const success = storage(`success-${questionId}`);
  const attempts = storage(`attempts-${questionId}`);

  let html = '<i class="fas fa-edit"></i> Нет попыток решения';
  if (success) {
    html = `<i class="fas fa-check"></i> Задача решена с ${attempts} попыт${attempts == 1? 'ки' : 'ок'}`;
  } else if (attempts > 0) {
    html = `<i class="fas fa-times"></i> Задача не решена с ${attempts} попыт${attempts == 1? 'ки' : 'ок'}`;
  }
  document.getElementById(`solution-${questionId}`).innerHTML = html;

  if (firstTime) {
    const resNode = document.getElementById(`checker-result-${questionId}`);
    resNode.innerHTML = lastOk? '<i class="fas fa-check"></i> Правильный ответ!' : '<i class="fas fa-times"></i> Неправильный ответ!';
    resNode.innerHTML += '<div class="checker-micro">(очистить поле ответа)</div>';
    document.getElementById(`checker-result-${questionId}`).style.display = '';
  }
};

const checkerButtons = document.getElementsByClassName('checker-button');
for (let i = 0; i < checkerButtons.length; ++i) {
  const b = checkerButtons[i];
  b.addEventListener('click', (event) => {
    const data = event.target.dataset;
    const answerUser = event.target.parentElement.getElementsByTagName('input')[0].value.trim();

    const successKey = `success-${data.questionId}`;
    const success = storage(successKey);

    if (success === false || success == null) {
      const attemtpsKey = `attempts-${data.questionId}`;
      storage(attemtpsKey, (storage(attemtpsKey) || 0) + 1);
    }

    let ok = answerUser == data.answer;
    if (data.questionType === 'numerical') {
      ok = check_float(answerUser, data.answer, data.tolerance);
    }
    storage(successKey, success || ok);

    const state = union(new Set(storage('modified-state') || []), new Set([+data.questionId]));
    storage('modified-state', [...state]);
    modifySubmits(data.questionId, true, ok);
    event.stopPropagation();
  });
}

const interactions = storage('modified-state') || [];
for (let i = 0; i < interactions.length; ++i) {
  modifySubmits(interactions[i]);
}

document.getElementById('reset-filters').addEventListener('click', (event) => {
  const checkboxes = filtersBox.getElementsByTagName('input');
  for (let i = 0; i < checkboxes.length; ++i) {
    checkboxes[i].checked = false;
  }
  for (let i = 0; i < questionElements.length; ++i) {
    questionElements[i].style.display = '';
  }
});

document.getElementById('reset-solutions').addEventListener('click', (event) => {
  Object.keys(localStorage)
        .filter((k) => k.startsWith('success-') || k.startsWith('attempts-'))
        .map((k) => localStorage.removeItem(k));
  
  const checkerResults = document.getElementsByClassName('checker-result');
  for (let i = 0; i < checkerResults.length; ++i) {
    checkerResults[i].style.display = 'none';
  }
  const solutionHistories = document.getElementsByClassName('solution-history');
  for (let i = 0; i < solutionHistories.length; ++i) {
    solutionHistories[i].innerHTML = '<i class="fas fa-edit"></i> Нет попыток решения';
  }
  const answerInputs = document.getElementsByClassName('checker-input');
  for (let i = 0; i < answerInputs.length; ++i) {
    answerInputs[i].value = '';
  }
  event.stopPropagation();
});

const checkerResults = document.getElementsByClassName('checker-result');
for (let i = 0; i < checkerResults.length; ++i) {
  checkerResults[i].addEventListener('click', (event) => {
    event.currentTarget.style.display = 'none';
    const id = +event.currentTarget.id.replace('checker-result-', '');
    document.getElementById(`check-input-${id}`).value = '';
  });
}

const checkerInput = document.getElementsByClassName('checker-input');
for (let i = 0; i < checkerInput.length; ++i) {
  checkerInput[i].addEventListener('keyup', (event) => {
    event.preventDefault();
    if (event.keyCode === 13) {
      const id = +event.currentTarget.id.replace('check-input-', '');
        document.getElementById(`check-button-${id}`).click();
    }
  });
}
