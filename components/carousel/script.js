(function(){
  var carousel = document.getElementById('my-carousel');
  if (!carousel) return;
  var track = carousel.querySelector('.carousel-track');
  var slides = carousel.querySelectorAll('.carousel-slide');
  var prevBtn = carousel.querySelector('.carousel-prev');
  var nextBtn = carousel.querySelector('.carousel-next');
  var dotsContainer = carousel.querySelector('.carousel-dots');
  var current = 0, total = slides.length, autoplayTimer;

  // 创建指示器
  for (var i = 0; i < total; i++) {
    var dot = document.createElement('span');
    dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
    dot.dataset.index = i;
    dotsContainer.appendChild(dot);
  }
  var dots = dotsContainer.querySelectorAll('.carousel-dot');

  function goTo(index) {
    if (index < 0) index = total - 1;
    if (index >= total) index = 0;
    current = index;
    track.style.transform = 'translateX(-' + (current * 100) + '%)';
    slides.forEach(function(s, i){ s.classList.toggle('active', i === current); });
    dots.forEach(function(d, i){ d.classList.toggle('active', i === current); });
  }

  prevBtn.addEventListener('click', function(){ goTo(current - 1); resetAutoplay(); });
  nextBtn.addEventListener('click', function(){ goTo(current + 1); resetAutoplay(); });
  dots.forEach(function(dot){
    dot.addEventListener('click', function(){ goTo(parseInt(dot.dataset.index)); resetAutoplay(); });
  });

  function resetAutoplay() {
    clearInterval(autoplayTimer);
    autoplayTimer = setInterval(function(){ goTo(current + 1); }, 5000);
  }
  resetAutoplay();
})();
