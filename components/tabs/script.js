(function(){
  var nav = document.querySelector('.tabs-nav');
  if (!nav) return;
  var btns = nav.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');
  btns.forEach(function(btn){
    btn.addEventListener('click', function(){
      btns.forEach(function(b){ b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });
      panels.forEach(function(p){ p.classList.remove('active'); });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      var target = document.getElementById(btn.getAttribute('data-tab'));
      if (target) target.classList.add('active');
    });
  });
})();
