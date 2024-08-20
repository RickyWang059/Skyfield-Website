//建立表單的監聽，讓使用者只能輸入指定的範圍，否則會跳出警告視窗並清空輸入欄位
document.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById('year').addEventListener('blur', validateYear);
  document.getElementById('month').addEventListener('blur', validateMonth);
  document.getElementById('day').addEventListener('blur', validateDay);
  document.getElementById('hour').addEventListener('blur', validateHour);
  document.getElementById('minute').addEventListener('blur', validateMinute);
  document.getElementById('altitude').addEventListener('blur', validateAltitude);
  document.getElementById('azimuth').addEventListener('blur', validateAzimuth);
});
//監聽年份在1550~2650年
function validateYear() {
  let year = document.getElementById('year').value;
  if (year && (year < 1550 || year > 2649)) {
    alert("年份必須在1550到2649之間");
    document.getElementById('year').value = '';
  }
}
//監聽月份在1~12月
function validateMonth() {
  let month = document.getElementById('month').value;
  if (month && (month < 1 || month > 12)) {
    alert("月份必須在1到12之間");
    document.getElementById('month').value = '';
  }
}
//監聽日期在1~31號
function validateDay() {
  let day = document.getElementById('day').value;
  if (day && (day < 1 || day > 31)) {
    alert("日期必須在1到31之間");
    document.getElementById('day').value = '';
  }
}
//監聽小時在0~23時
function validateHour() {
  let hour = document.getElementById('hour').value;
  if (hour && (hour < 0 || hour > 23)) {
    alert("小時必須在0到23之間");
    document.getElementById('hour').value = '';
  }
}
//監聽分鐘在0~59分
function validateMinute() {
  let minute = document.getElementById('minute').value;
  if (minute && (minute < 0 || minute > 59)) {
    alert("分鐘必須在0到59之間");
    document.getElementById('minute').value = '';
  }
}
//監聽仰角在0~90
function validateAltitude() {
  let altitude = document.getElementById('altitude').value;
  if (altitude && (altitude < 0 || altitude > 90)) {
    alert("仰角必須在0到90之間");
    document.getElementById('altitude').value = '';
  }
}
//監聽方位角在0~360
function validateAzimuth() {
  let azimuth = document.getElementById('azimuth').value;
  if (azimuth && (azimuth < 0 || azimuth > 360)) {
    alert("方位角必須在0到360之間");
    document.getElementById('azimuth').value = '';
  }
}