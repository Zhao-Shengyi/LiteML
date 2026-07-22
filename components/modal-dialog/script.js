(function(){
  var dialog = document.getElementById('my-modal');
  if (!dialog) return;
  var openers = document.querySelectorAll('[data-open-modal="my-modal"]');
  var closeBtns = dialog.querySelectorAll('.modal-close, .modal-cancel');

  openers.forEach(function(btn){
    btn.addEventListener('click', function(){ dialog.showModal(); });
  });
  closeBtns.forEach(function(btn){
    btn.addEventListener('click', function(){ dialog.close(); });
  });
  dialog.addEventListener('click', function(e){
    if (e.target === dialog) dialog.close();
  });
})();
