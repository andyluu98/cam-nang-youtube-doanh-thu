// Lưu tiến độ checklist và tô sáng mục lục theo vị trí cuộn
(function () {
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* bỏ qua khi trình duyệt chặn */ } }

  document.querySelectorAll('.checklist input[data-key]').forEach(function (box) {
    var key = 'cnyt-' + box.dataset.key;
    box.checked = get(key) === '1';
    box.addEventListener('change', function () { set(key, box.checked ? '1' : '0'); });
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        links.forEach(function (a) { a.classList.remove('active'); });
        var a = byId[e.target.id];
        if (a) a.classList.add('active');
      }
    });
  }, { rootMargin: '-90px 0px -70% 0px' });
  document.querySelectorAll('main h2[id]').forEach(function (h) { obs.observe(h); });
})();
