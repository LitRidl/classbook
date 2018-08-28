const { ipcRenderer, clipboard, remote } = require('electron');
const Excel = require('exceljs');
const searchInPage = require('electron-in-page-search').default;
require('pdfmake');


/* ------------- */
/* Common logics */
/* ------------- */
const storage = (key, value) => {
  if (value === undefined) {
    const item = localStorage.getItem(key);
    return item === null ? null : JSON.parse(item);
  }
  localStorage.setItem(key, JSON.stringify(value));
  return value;
};

const checkFloat = (answer, correct, tolerance) => {
  const a = +(typeof answer === 'string' ? answer.replace(',', '.') : answer);
  const c = +(typeof correct === 'string' ? correct.replace(',', '.') : correct);
  const t = +(typeof tolerance === 'string' ? tolerance.replace(',', '.') : tolerance);
  if (tolerance === 'null') {
    return a === c;
  }
  return a >= c - t && a <= c + t;
};

const numberPlural = (n, titles) => {
  const cases = [2, 0, 1, 1, 1, 2];
  if (n == 0) return titles[2];
  return titles[
    n % 100 > 4 && n % 100 < 20 ? 2 : cases[n % 10 < 5 ? n % 10 : 5]
  ];
};

const union = (setA, setB) => {
  const united = new Set(setA);
  for (const elem of setB) {
    united.add(elem);
  }
  return united;
};

function intersection(setA, setB) {
  const intersected = new Set();
  for (const elem of setB) {
    if (setA.has(elem)) {
      intersected.add(elem);
    }
  }
  return intersected;
}


/* ---------------- */
/* Contacts buttons */
/* ---------------- */
const pdfBtn = document.getElementById('button-pdf');
pdfBtn.addEventListener('click', (event) => {
  ipcRenderer.send('print-to-pdf');
});

const siteBtn = document.getElementById('copy-site');
siteBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-site').innerText);
});

const emailBtn = document.getElementById('copy-email');
emailBtn.addEventListener('click', () => {
  clipboard.writeText(document.getElementById('contacts-email').innerText);
});

/* ---------------- */
/*    Data model    */
/* ---------------- */
// const questionsData, dataVersion, questionsIndex (in html)
const questionElements = document.getElementsByClassName('question');
const allQuestions = {};
const allQuestionsIdx = [];
for (let i = 0; i < questionElements.length; ++i) {
  const q = questionElements[i];
  allQuestions[+q.dataset.questionId] = q;
  allQuestionsIdx.push(+q.dataset.questionId);
}
allQuestionsIdx.sort();


/* ----------------- */
/* Filter checkboxes */
/* ----------------- */
const filtersBox = document.getElementById('filters-box');
const fieldsets = filtersBox.getElementsByTagName('fieldset');

const checkboxGroups = [];
for (let i = 0; i < fieldsets.length; i++) {
  const cbs = fieldsets[i].getElementsByTagName('input');
  checkboxGroups.push(cbs);
}

const totalsLabel = document.getElementById('totals-label');
const updateQuestionsShownStats = (filtered, total) => {
  const filteredWord = numberPlural(filtered, ['Показана', 'Показаны', 'Показано']);
  const tasksWord = numberPlural(filtered, ['задача', 'задачи', 'задач']);
  const totalTpl = `${filteredWord} <span class="total-filtered">${filtered}</span> ${tasksWord} из <span class="total-all">${total}</span>`;
  totalsLabel.innerHTML = totalTpl;
};

const userChangedFiltersHandler = () => {
  let questions = new Set(allQuestionsIdx);
  for (let g = 0; g < checkboxGroups.length; ++g) {
    let questionsLocal = new Set();
    let groupHasCheckedFilter = false;
    for (let i = 0; i < checkboxGroups[g].length; ++i) {
      const cb = checkboxGroups[g][i];
      if (cb.checked) {
        groupHasCheckedFilter = true;
        questionsLocal = union(questionsLocal, new Set(questionsIndex[cb.name][cb.value]));
      }
    }
    if (groupHasCheckedFilter) {
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
  updateQuestionsShownStats(questions.size, allQuestionsIdx.length);
};


const persistFiltersState = () => {
  const filterCheckboxes = document.getElementsByClassName('filter-item-input');
  const filtersChecked = {};
  for (let i = 0; i < filterCheckboxes.length; ++i) {
    filtersChecked[filterCheckboxes[i].id] = filterCheckboxes[i].checked;
  }
  storage('filters-checked', filtersChecked);
};

const loadFiltersStateToHtml = () => {
  const filtersChecked = storage('filters-checked') || {};
  Object.entries(filtersChecked).forEach(([filterId, isChecked]) => {
    document.getElementById(filterId).checked = isChecked;
  });
};

loadFiltersStateToHtml(); // MUST go before onChange handler!!! otherwise infinite recursion
userChangedFiltersHandler();

// User clicked filter checkboxes
filtersBox.addEventListener('change', (event) => {
  userChangedFiltersHandler();
  persistFiltersState();
  event.stopPropagation();
});


// Reset filters function
const resetFilters = () => {
  const checkboxes = filtersBox.getElementsByTagName('input');
  for (let i = 0; i < checkboxes.length; ++i) {
    checkboxes[i].checked = false;
  }
  for (let i = 0; i < questionElements.length; ++i) {
    questionElements[i].style.display = '';
  }
  persistFiltersState();
  updateQuestionsShownStats(allQuestionsIdx.length, allQuestionsIdx.length);
};

// User clicked filters reset
document.getElementById('reset-filters').addEventListener('click', (event) => {
  resetFilters();
  event.stopPropagation();
});


/* ----------------- */
/*  Modify submits   */
/* ----------------- */
const setQuestionAttemptStatusHtml = (questionId, afterSubmitClicked, lastOk) => {
  const success = storage(`success-${questionId}`);
  const attempts = storage(`attempts-${questionId}`);

  let html = '<i class="fas fa-edit"></i> Нет попыток решения';
  if (success) {
    html = `<i class="fas fa-check"></i> Задача решена с ${attempts} попыт${
      attempts == 1 ? 'ки' : 'ок'
    }`;
  } else if (attempts > 0) {
    html = `<i class="fas fa-times"></i> Задача не решена с ${attempts} попыт${
      attempts == 1 ? 'ки' : 'ок'
    }`;
  }
  document.getElementById(`solution-${questionId}`).innerHTML = html;

  if (afterSubmitClicked) {
    const resNode = document.getElementById(`checker-result-${questionId}`);
    var contents = lastOk
      ? '<i class="fas fa-check"></i> Правильный ответ!'
      : '<i class="fas fa-times"></i> Неправильный ответ!';
    contents += '<div class="checker-micro">(нажмите чтобы очистить поле ответа)</div>';
    resNode.innerHTML = contents;
    document.getElementById(`checker-result-${questionId}`).style.display = '';
  }
};


/* ---------------------- */
/* Handle clicking Submit */
/* ---------------------- */
const submitSolutionButtonClicked = (event) => {
  const data = event.target.dataset;
  const answerUser = event.target.parentElement.getElementsByTagName('input')[0].value.trim();

  const successKey = `success-${data.questionId}`;
  const successInThePast = storage(successKey);

  if (successInThePast === false || successInThePast == null) {
    const attemtpsKey = `attempts-${data.questionId}`;
    storage(attemtpsKey, (storage(attemtpsKey) || 0) + 1);
  }

  let solutionIsCorrect = (answerUser == data.answer);
  if (data.questionType === 'numerical') {
    solutionIsCorrect = checkFloat(answerUser, data.answer, data.tolerance);
  }
  storage(successKey, successInThePast || solutionIsCorrect);

  const questionsWithAttempts = union(new Set(storage('questions-with-attempts') || []), new Set([+data.questionId]));
  storage('questions-with-attempts', [...questionsWithAttempts]);
  setQuestionAttemptStatusHtml(data.questionId, true, solutionIsCorrect); // afterSubmitClicked = true
  event.stopPropagation();
};
const submitSolutionButtons = document.getElementsByClassName('checker-button');
for (let i = 0; i < submitSolutionButtons.length; ++i) {
  const b = submitSolutionButtons[i];
  b.addEventListener('click', submitSolutionButtonClicked);
}


/* ----------------------- */
/* Loading from LS to HTML */
/* ----------------------- */
const loadAttemptsToHtml = () => {
  const submittedTasks = storage('questions-with-attempts') || [];
  for (let i = 0; i < submittedTasks.length; ++i) {
    setQuestionAttemptStatusHtml(submittedTasks[i]);
  }
};
// Extract all attempts from LS and set html
loadAttemptsToHtml();


/* ----------------- */
/* Filter checkboxes */
/* ----------------- */
const solutionHistories = document.getElementsByClassName('solution-history');
const answerInputs = document.getElementsByClassName('checker-input');
const afterSubmitAttemptResult = document.getElementsByClassName('checker-result');
const resetSolutions = () => {
  Object.keys(localStorage).filter(k => k.startsWith('success-') || k.startsWith('attempts-')).map(k => localStorage.removeItem(k));
  localStorage.removeItem('questions-with-attempts');
  localStorage.removeItem('data-version');
  localStorage.removeItem('filters-checked');

  for (let i = 0; i < afterSubmitAttemptResult.length; ++i) {
    afterSubmitAttemptResult[i].style.display = 'none';
  }
  for (let i = 0; i < solutionHistories.length; ++i) {
    solutionHistories[i].innerHTML = '<i class="fas fa-edit"></i> Нет попыток решения'; // REFACTOR
  }
  for (let i = 0; i < answerInputs.length; ++i) {
    answerInputs[i].value = '';
  }
};

// User clicks Reset All Solutions
document.getElementById('reset-solutions').addEventListener('click', (event) => {
  resetSolutions();
});

/* ---------------------------------------------------------- */
/* Purging LS if old or empty data version + set data version */
/* ---------------------------------------------------------- */
const purgeDataIfOldVersion = () => {
  if (!storage('data-version') || (storage('data-version') != dataVersion)) {
    resetSolutions();
    resetFilters(); // TODO: filters persistence
  }
  // const good = true;
  // const questionsWithAttempts = storage('questions-with-attempts') || [];
  // for (let i = 0; i < questionsWithAttempts.length; ++i) {
  //   if (!storage(`success-${questionsWithAttempts[i]}`) || storage(`attempts-${questionsWithAttempts[i]}`) == null) {
  //     good = false;
  //   }
  // }
  // if (!good) {
  //   resetSolutions();
  //   resetFilters(); // TODO: filters persistence
  // }
  storage('data-version', dataVersion);
};
purgeDataIfOldVersion();


/* -------------------------------------- */
/* When user clicks on attempt to hide it */
/* -------------------------------------- */
// const afterSubmitAttemptResult = document.getElementsByClassName('checker-result');
const afterSubmitAttemptResultClicked = (event) => {
  event.currentTarget.style.display = 'none';
  const id = +event.currentTarget.id.replace('checker-result-', '');
  if (document.getElementById(`check-input-${id}`)) {
    document.getElementById(`check-input-${id}`).value = '';
    document.getElementById(`check-input-${id}`).focus();
  }
};
for (let i = 0; i < afterSubmitAttemptResult.length; ++i) {
  afterSubmitAttemptResult[i].addEventListener('click', afterSubmitAttemptResultClicked);
}

/* ------------------------------------- */
/* Submit attempt when user clicks Enter */
/* ------------------------------------- */
const checkerInput = document.getElementsByClassName('checker-input');
const checkerInputPressed = (event) => {
  event.preventDefault();
  if (event.keyCode === 13) {
    const id = +event.currentTarget.id.replace('check-input-', '');
    document.getElementById(`check-button-${id}`).click();
  }
};
for (let i = 0; i < checkerInput.length; ++i) {
  checkerInput[i].addEventListener('keyup', checkerInputPressed);
}


// /////////////////////////////////////// //
// SEARCH BOX

const inPageSearch = searchInPage(remote.getCurrentWebContents());

document.getElementById('butt').addEventListener('click', () => {
  inPageSearch.openSearchWindow();
});


// /////////////////////////////////////// //
// EXCEL block


const excelSubmitButtonChanged = (e) => {
  e.stopPropagation();
  const data = e.target.dataset;
  let solutionSheetFound = true;
  document.getElementById(`checker-result-${data.questionId}`).style.display = 'none';
  const f = e.target.files[0];
  if (!f) {
    return;
  }
  const reader = new FileReader();
  reader.onload = (re) => {
    const wb = new Excel.Workbook();
    wb.xlsx.load(re.target.result).then(() => {
      solutionSheetFound = false;
      let solutionIsCorrect = false;
      wb.eachSheet((ws, wsId) => {
        if (ws.name.includes('(решение)')) {
          solutionSheetFound = true;
          solutionIsCorrect = ws.getCell('C1').value.result === 'решена';
        }
      });

      if (!solutionSheetFound) {
        throw Error('Некорректный формат файла');
      }

      const successKey = `success-${data.questionId}`;
      const successInThePast = storage(successKey);
      if (successInThePast === false || successInThePast == null) {
        const attemtpsKey = `attempts-${data.questionId}`;
        storage(attemtpsKey, (storage(attemtpsKey) || 0) + 1);
      }

      storage(successKey, successInThePast || solutionIsCorrect);

      const questionsWithAttempts = union(new Set(storage('questions-with-attempts') || []), new Set([+data.questionId]));
      storage('questions-with-attempts', [...questionsWithAttempts]);
      setQuestionAttemptStatusHtml(data.questionId, true, solutionIsCorrect); // afterSubmitClicked = true

      // const ws2 = wb.getWorksheet('Расход электроэнергии');
      // console.log(ws2.getCell('D13').value.result);
    }).catch((reason) => {
      const resNode = document.getElementById(`checker-result-${data.questionId}`);
      resNode.innerHTML = '<i class="fas fa-times"></i> Ошибка при чтении файла!';
      if (!solutionSheetFound) {
        resNode.innerHTML = '<i class="fas fa-times"></i> Файл не соответсвует условию!';
      }
      resNode.innerHTML += '<div class="checker-micro">(нажмите чтобы скрыть ошибку)</div>';
      document.getElementById(`checker-result-${data.questionId}`).style.display = '';
    });
  };
  reader.readAsArrayBuffer(f);
};
const excelSubmitButtons = document.getElementsByClassName('checker-input-file');
for (let i = 0; i < excelSubmitButtons.length; ++i) {
  excelSubmitButtons[i].addEventListener('change', excelSubmitButtonChanged);
}


// DIFFERENT BLOCK, REPORTING ONLY


/* ------------------------------ */
/* Generating statistical reports */
/* ------------------------------ */
const generateStatsBody = (() => {
  const questionIds = storage('questions-with-attempts') || [];
  questionIds.sort();

  const topicQuestions = {};
  for (let qIdIdx = 0; qIdIdx < questionIds.length; ++qIdIdx) {
    const q = questionsData[questionIds[qIdIdx]];

    for (let topicIdx = 0; topicIdx < q.topics_informatics.length; ++topicIdx) {
      const topic = q.topics_informatics[topicIdx];
      if (!topicQuestions.hasOwnProperty(topic)) {
        topicQuestions[topic] = [];
      }
      topicQuestions[topic].push(q);
      topicQuestions[topic].sort((l, r) => {
        const sL = storage(`success-${l.question_id}`);
        const sR = storage(`success-${r.question_id}`);
        return -(sL - sR) || l.name.localeCompare(r.name);
      });
    }
  }

  const body = [];
  // For order consistency
  let totalG = 0;
  let solvedG = 0;
  let solvingG = 0;
  let triesSumG = 0.0;
  let difficultySumG = 0.0;
  const allTopics = ['Информация и информационные процессы', 'Алгоритмизация и программирование', 'Моделирование и формализация', 'Обработка числовых данных в электр. таблицах', 'Измерение количества информации', 'Информационная безопасность'];
  for (let topicIdx = 0; topicIdx < allTopics.length; ++topicIdx) {
    if (topicQuestions.hasOwnProperty(allTopics[topicIdx])) {
      const qs = topicQuestions[allTopics[topicIdx]];
      if (qs.length < 1) { continue; }
      let total = 0;
      let solved = 0;
      let solving = 0;
      for (let qIdx = 0; qIdx < qs.length; ++qIdx) {
        const q = qs[qIdx];
        if (q.type === 'numerical' || q.type === 'excel') {
          ++total;
          if (storage(`success-${q.question_id}`)) {
            ++solved;
            triesSumG += storage(`attempts-${q.question_id}`);
            difficultySumG += { 'Базовый уровень': 1, 'Повышенный уровень': 2, 'Высокий уровень': 3 }[q.difficulty] || 1;
          } else if (storage(`attempts-${q.question_id}`) > 0) {
            ++solving;
          }
        }
      }
      totalG += total; solvedG += solved; solvingG += solving;
      const totalWord = numberPlural(total, ['задача', 'задачи', 'задач']);
      const solvedWord = numberPlural(solved, ['решена', 'решены', 'решено']);
      const solvingWord = numberPlural(solving, ['решается', 'решаются', 'решается']);
      const stats = ` (${total} ${totalWord}: ${solved} ${solvedWord}, ${solving} ${solvingWord})`; // , ${notSolved} не решалась)`;
      body.push([{ colSpan: 3, text: [{ text: allTopics[topicIdx], style: 'topicName' }, { text: stats, style: 'topicStats' }], margin: [0, 10, 0, 2] }, '', '']);
      for (let qIdx = 0; qIdx < qs.length; ++qIdx) {
        const q = qs[qIdx];
        if (storage(`success-${q.question_id}`) === null || storage(`attempts-${q.question_id}`) === null) {
          continue;
        }
        const name = q.name;
        const bStar = { text: '\uf005', font: 'fas' };
        const wStar = { text: '\uf005', font: 'far' };
        const difficulty = ({
          'Базовый уровень': [bStar, wStar, wStar],
          'Повышенный уровень': [bStar, bStar, wStar],
          'Высокий уровень': [bStar, bStar, bStar],
        }[q.difficulty] || 'Сложность неизвестна');
        const success = storage(`success-${q.question_id}`) ? 'Решена' : 'Решается';
        const tries = storage(`attempts-${q.question_id}`);
        const triesWord = numberPlural(tries, ['попытка', 'попытки', 'попыток']);
        const starsStyle = storage(`success-${q.question_id}`) ? 'starsG' : 'starsY';
        body.push([{ text: name, style: 'qName' }, { text: difficulty, style: starsStyle }, { text: `${success}, ${tries} ${triesWord}`, style: 'tries' }]);
      }
    }
  }

  const totalWord = numberPlural(totalG, ['задача', 'задачи', 'задач']);
  const solvedWord = numberPlural(solvedG, ['решена', 'решены', 'решено']);
  const solvingWord = numberPlural(solvingG, ['решается', 'решаются', 'решается']);
  const stats = `Всего ${totalG} ${totalWord}: ${solvedG} ${solvedWord}, ${solvingG} ${solvingWord}.`; // , ${notSolved} не решалась)`;
  const avgTries = (solvedG != 0) ? (`— ${(1.0 * triesSumG / solvedG).toFixed(1).replace('.', ',')}`) : 'неизвестно';
  const avgDifficulty = (solvedG != 0) ? (`— ${(1.0 * difficultySumG / solvedG).toFixed(1).replace('.', ',')}`) : 'неизвестна';
  if (body.length > 0) {
    return [
      { text: stats, style: 'globalStats' },
      { text: `Средняя сложность решённых задач ${avgDifficulty}.`, style: 'globalStats' },
      { text: `Среднее количество попыток для решённых задач ${avgTries}.`, style: 'globalStats', margin: [0, 0, 0, 5] },
      {
        layout: 'noBorders',
        table: {
          widths: ['*', 50, 110],
          body,
        },
      },
    ];
  }
  return { text: 'Нет попыток решения ни по одной задаче', style: 'noData' };
});

function uuid4char() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16),
  ).substr(0, 4).toUpperCase();
}

const generatePdf = (momentStr, uuid) => {
  const docDefinition = {
    info: {
      title: 'Финграмотность, Статистика решений',
      author: 'Приложение Финансовая Грамотность',
      creator: 'Приложение Финансовая Грамотность',
      producer: 'Приложение Финансовая Грамотность',
    },
    header: {
      columns: [
        { text: momentStr, margin: [10, 10, 0, 0], fontSize: 10, color: 'gray' },
        { text: `${uuid}`, margin: [0, 10, 10, 0], fontSize: 10, color: 'gray', alignment: 'right' },
      ],
    },
    footer: ((currentPage, pageCount) => ({
      columns: [
          // { text: 'ПАКК', margin: [10, 0, 0, 0], fontSize: 10, color: 'gray' },
          { text: `Стр. ${currentPage.toString()} из ${pageCount}`, fontSize: 10, color: 'gray', alignment: 'center' },
          // { text: 'Минфин', alignment: 'right', margin: [0, 0, 10, 0], fontSize: 10, color: 'gray' },
        ],
    })),
    content: [
      { image: 'data:image/png;base64,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', fit: [60, 60], alignment: 'center' },
      { text: 'Отчёт об успешности работы', style: 'globalHeader' },
      generateStatsBody(),
    ],
    styles: {
      th: { bold: true, alignment: 'center' },
      tagr: { bold: true, alignment: 'right' },
      tcell: { bold: true, alignment: 'right' },
      topicName: { bold: true, fontSize: 10 },
      topicStats: { color: 'gray', bold: false, fontSize: 10 },
      noData: { bold: true, alignment: 'center', fontSize: 14 },
      qName: { margin: [10, 0, 0, 0], fontSize: 10 },
      starsG: { fontSize: 10, alignment: 'center', color: '#b0ce94' },
      starsY: { fontSize: 10, alignment: 'center', color: '#f8d776' },
      tries: { fontSize: 10 },
      globalHeader: { fontSize: 16, bold: true, alignment: 'center', margin: [0, 0, 0, 27] },
      globalStats: { fontSize: 12, bold: false },
    },
  };
  return docDefinition;
};


document.getElementById('download-stats').addEventListener('click', (event) => {
  pdfMake.fonts = {
    fas: {
      normal: 'fas.ttf',
      bold: 'fas.ttf',
      italics: 'fas.ttf',
      bolditalics: 'fas.ttf',
    },
    far: {
      normal: 'far.ttf',
      bold: 'far.ttf',
      italics: 'far.ttf',
      bolditalics: 'far.ttf',
    },
    Roboto: {
      normal: 'Roboto-Regular.ttf',
      bold: 'Roboto-Medium.ttf',
      italics: 'Roboto-Italic.ttf',
      bolditalics: 'Roboto-MediumItalic.ttf',
    },
  };
  const formatterDate = new Intl.DateTimeFormat('ru', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  });
  const formatterTime = new Intl.DateTimeFormat('ru', {
    hour: 'numeric',
    minute: 'numeric',
  });

  const moment = new Date();
  const momentStr = `${formatterDate.format(moment).replace(' г.', '')} в ${formatterTime.format(moment)}`;
  const uuid = uuid4char();

  pdfMake.createPdf(generatePdf(momentStr, uuid)).download(`Финграмотность, ${momentStr.replace(':', '-')}.pdf`);
});
