(function(){
  var headers = document.querySelectorAll('.accordion-header');
  headers.forEach(function(header){
    header.addEventListener('click', function(){
      var expanded = header.getAttribute('aria-expanded') === 'true';
      header.setAttribute('aria-expanded', String(!expanded));
      header.nextElementSibling.classList.toggle('open');
    });
  });
})();
