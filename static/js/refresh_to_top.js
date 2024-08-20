//重新整理時，頁面會回到頂部
window.onload = function () {
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  window.scrollTo(0, 0);
}
