const Excel = require('exceljs');

const wb = new Excel.Workbook();
wb.xlsx.readFile('../Расход электроэнергии.xlsx').then(() => {
  let foundSolution = false;
  wb.eachSheet((ws, wsId) => {
    if (ws.name.includes('(решение)')) {
      console.log(ws.getCell('C1').value.result === 'решена');
      foundSolution = true;
    }
  });

  // const ws2 = wb.getWorksheet('Расход электроэнергии');
  // console.log(ws2.getCell('D13').value.result);
}).catch((reason) => {
  console.log(reason);
});
