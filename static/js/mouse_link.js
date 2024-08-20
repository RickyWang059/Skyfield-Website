//建立鼠標移至超連結時之動作
let links = document.querySelectorAll("a");

// 監聽每個超連結的 mouseover 事件
links.forEach(link => {
  link.addEventListener("mouseover", function () {
    // 改變特殊鼠標的尺寸
    myCursor.style.width = "65px";
    myCursor.style.height = "65px";
    circle.style.width = "0px";
    circle.style.height = "0px";
    circle.style.boxShadow = "none";
    // 獲取超連結的自定義文字內容屬性
    let customText = link.getAttribute("data-text");

    // 創建一個新的文字元素，並設置超連結的自定義文字內容
    let textElement = document.createElement("div");
    textElement.textContent = customText;
    textElement.classList.add("cursor-text"); // 添加一個 CSS 類名以便於樣式設置

    // 將文字元素添加到 myCursor 中
    cursor.appendChild(textElement);
  });

  // 監聽 mouseout 事件以移除文字元素
  link.addEventListener("mouseout", function () {
    myCursor.style.width = "40px";
    myCursor.style.height = "40px";
    circle.style.width = "24px";
    circle.style.height = "24px";
    circle.style.boxShadow ="0px 0px 10px 2px rgba(250, 150, 50, 0.8), 0px 0px 20px 5px rgba(250, 102, 59, 0.6), 0px 0px 30px 10px rgba(250, 102, 59, 0.4)";
    let textElement = document.querySelector(".cursor-text");
    if (textElement) {
      textElement.remove(); // 移除文字元素
    }
  });
});