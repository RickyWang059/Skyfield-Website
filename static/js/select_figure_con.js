//建立四選一的圖片選擇按鈕，預設只顯示第一張圖
function showContent(contentId) {
    // 隱藏所有圖片
    var contents = document.querySelectorAll('.classification');
    contents.forEach(function(content) {
        content.style.display = 'none';
    });

    // 只顯示指定的圖片
    var selectedContent = document.getElementById(contentId);
    selectedContent.style.display = 'block';
}

// 預設顯示第一張圖
showContent('1');