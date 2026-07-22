(function(){
  var btn = document.querySelector('.navbar-toggle');
  var menu = document.querySelector('.navbar-menu');
  if (btn && menu) {
    btn.addEventListener('click', function(){ menu.classList.toggle('open'); });
  }
})();
