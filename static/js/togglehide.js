//隱藏區塊，點選按鈕時出現
function toggleHide(id) {
  event.preventDefault();
  var element = document.getElementById(id);
  if (element.style.display === 'none') {
    element.style.display = '';
  } else {
    element.style.display = 'none';
  }
}