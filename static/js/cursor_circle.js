//建立主要鼠標myCursor與外圈circle之移動監聽
let cursor = document.getElementById("myCursor");
let circle = document.getElementById("circle");
window.addEventListener("mousemove", function (e) {
  let x = e.clientX;
  let y = e.clientY;
  cursor.style.left = x - 20 + "px";
  cursor.style.top = y - 20 + "px";
  circle.style.left = x - 12 + "px";
  circle.style.top = y - 12 + "px";
});

window.addEventListener("scroll", function (e) {
  let x = event.clientX;
  let y = event.clientY;
  cursor.style.left = x - 20 + "px";
  cursor.style.top = y - 20 + "px";
  circle.style.left = x - 12 + "px";
  circle.style.top = y - 12 + "px";
})