(function () {
  var input = document.getElementById('site-search-input');
  var list = document.getElementById('site-search-results');
  if (!input || !list) return;
  var index = null, loading = false, active = -1;

  function load(cb) {
    if (index) return cb();
    if (loading) return;
    loading = true;
    fetch('/assets/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { index = d; cb(); })
      .catch(function () { loading = false; });
  }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var hits = [];
    index.forEach(function (p) {
      var title = p.t.toLowerCase(), rest = p.x.toLowerCase(), score = 0;
      for (var i = 0; i < terms.length; i++) {
        var inTitle = title.indexOf(terms[i]) > -1;
        if (!inTitle && rest.indexOf(terms[i]) === -1) return;
        score += inTitle ? 3 : 1;
      }
      hits.push({ p: p, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    return hits.slice(0, 6).map(function (h) { return h.p; });
  }

  function render() {
    var q = input.value.trim();
    active = -1;
    if (!q) { list.hidden = true; list.innerHTML = ''; return; }
    var hits = search(q);
    list.innerHTML = hits.length
      ? hits.map(function (p) {
          var a = document.createElement('a');
          a.href = '/' + p.s + '/';
          a.textContent = p.t;
          var li = document.createElement('li');
          li.appendChild(a);
          return li.outerHTML;
        }).join('')
      : '<li class="site-search-empty">No pages match that search.</li>';
    list.hidden = false;
  }

  function move(step) {
    var links = list.querySelectorAll('a');
    if (!links.length) return;
    active = (active + step + links.length) % links.length;
    links[active].focus();
  }

  input.addEventListener('focus', function () { load(render); });
  input.addEventListener('input', function () { load(render); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { list.hidden = true; }
    else if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'Enter') {
      var first = list.querySelector('a');
      if (first) { e.preventDefault(); location.href = first.href; }
    }
  });
  list.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); active === 0 ? input.focus() : move(-1); }
    else if (e.key === 'Escape') { list.hidden = true; input.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.site-search')) list.hidden = true;
  });
})();
