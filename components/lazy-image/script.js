(function(){
  var observer = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if (!entry.isIntersecting) return;
      var img = entry.target;
      var src = img.getAttribute('data-src');
      if (!src) return;
      img.src = src;
      img.addEventListener('load', function(){ img.classList.add('loaded'); });
      img.addEventListener('error', function(){ img.classList.add('error'); img.alt = '加载失败'; });
      observer.unobserve(img);
    });
  }, { rootMargin: '200px' });
  document.querySelectorAll('.lazy-img').forEach(function(img){ observer.observe(img); });
})();
