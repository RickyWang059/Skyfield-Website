//建立三選一的選擇區塊按鈕，預設顯示第一區塊
function showContent(contentId) {
    // 隱藏所有內容
    var contents = document.querySelectorAll('.classification');
    contents.forEach(function(content) {
        content.classList.remove('active');
    });

    // 只顯示指定的區塊  
    var selectedContent = document.getElementById(contentId);
    selectedContent.classList.add('active');
}

// 顯示第一區塊
showContent('season');