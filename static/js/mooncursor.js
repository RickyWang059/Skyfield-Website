//建立preface頁面的月亮鼠標的移動監聽
let cursor = document.getElementById("MoonCursor");

window.addEventListener("mousemove", function (e) {
  let x = e.clientX;
  let y = e.clientY;
  cursor.style.left = x - 25 + "px";
  cursor.style.top = y - 25 + "px"
});