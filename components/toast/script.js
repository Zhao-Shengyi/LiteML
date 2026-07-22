(function(){
  window.LiteToast = {
    show: function(msg, type, duration){
      type = type || 'info';
      duration = duration || 3000;
      var container = document.getElementById('toast-container');
      if (!container) return;
      var el = document.createElement('div');
      el.className = 'toast toast-' + type;
      el.textContent = msg;
      container.appendChild(el);
      setTimeout(function(){
        el.classList.add('toast-out');
        setTimeout(function(){ el.remove(); }, 300);
      }, duration);
    },
    success: function(msg, d) { this.show(msg, 'success', d); },
    error:   function(msg, d) { this.show(msg, 'error',   d); },
    warning: function(msg, d) { this.show(msg, 'warning', d); },
    info:    function(msg, d) { this.show(msg, 'info',    d); }
  };
})();
