var ua = navigator.userAgent;
var ipad = ua.match(/(iPad).*OS\s([\d_]+)/),
    isIphone = !ipad && ua.match(/(iPhone\sOS)\s([\d_]+)/),
    isAndroid = ua.match(/(Android)\s+([\d.]+)/),
    isMobile = isIphone || isAndroid;

if (isMobile) {
    var deviceWidth = document.documentElement.clientWidth;
    var deviceWidth2 = window.screen.width;
    console.log(deviceWidth2);
    console.log(deviceWidth);
    
    var scale = deviceWidth / 1200;
    console.log(scale);
    
    document.getElementById("view").setAttribute('content', "user-scalable=yes, width=device-width, initial-scale=" + scale);
} else {
    // 桌面設備的處理邏輯
}
