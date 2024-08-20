//返回頂部之超連結按鈕
$(function () {
  $('#BackTop').click(function () {
    $('html,body').animate({scrollTop: 0}, 333);
  });
  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      $('#BackTop').fadeIn(222);
    } else {
      $('#BackTop').stop().fadeOut(222);
    }
  }).scroll();
});