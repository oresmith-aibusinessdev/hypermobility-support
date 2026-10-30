(function () {
  var form = document.getElementById("site-search");
  if (!form) return;
  var box = document.getElementById("site-search-box");
  var out = document.getElementById("site-search-results");
  var index = null, loading = null, active = -1, current = [];
  form.hidden = false;

  function load() {
    if (!loading) {
      loading = fetch("/assets/search-index.json").then(function (r) { return r.json(); })
        .then(function (d) { index = d; return d; })
        .catch(function () { loading = null; });
    }
    return loading;
  }
  function esc(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function escRe(t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean), hits = [];
    if (!terms.length) return hits;
    index.forEach(function (d) {
      var t = d.title.toLowerCase(), e = d.eyebrow.toLowerCase(), h = d.headings.toLowerCase(), b = d.body.toLowerCase(), score = 0;
      for (var i = 0; i < terms.length; i++) {
        var w = terms[i], s = 0, at, n = 0;
        if (t.indexOf(w) > -1) s += 10;
        if (e.indexOf(w) > -1) s += 5;
        if (h.indexOf(w) > -1) s += 4;
        at = b.indexOf(w);
        while (at > -1 && n < 5) { n++; at = b.indexOf(w, at + 1); }
        s += n;
        if (!s) return;
        score += s;
      }
      hits.push({ doc: d, score: score, terms: terms });
    });
    return hits.sort(function (a, b) { return b.score - a.score; }).slice(0, 8);
  }

  function snippet(d, terms) {
    var low = d.body.toLowerCase(), pos = -1;
    for (var i = 0; i < terms.length && pos < 0; i++) pos = low.indexOf(terms[i]);
    if (pos < 0) return esc(d.body.slice(0, 120)) + "&hellip;";
    var start = Math.max(0, pos - 50), re = new RegExp("(" + terms.map(escRe).join("|") + ")", "gi");
    return (start > 0 ? "&hellip;" : "") + esc(d.body.slice(start, pos + 90)).replace(re, "<mark>$1</mark>") + "&hellip;";
  }

  function render() {
    var q = box.value.trim();
    active = -1;
    if (!q || !index) { out.hidden = true; out.innerHTML = ""; return; }
    current = search(q);
    out.hidden = false;
    out.innerHTML = current.length ? current.map(function (h, i) {
      return '<a class="sr-item" role="option" id="sr-' + i + '" href="' + h.doc.url + '">' +
        '<span class="sr-eyebrow">' + esc(h.doc.eyebrow) + '</span>' +
        '<span class="sr-title">' + esc(h.doc.title) + '</span>' +
        '<span class="sr-snip">' + snippet(h.doc, h.terms) + '</span></a>';
    }).join("") : '<p class="sr-none">No pages match. Try a shorter or different word.</p>';
  }

  function setActive(i) {
    var items = out.querySelectorAll(".sr-item");
    if (!items.length) return;
    active = (i + items.length) % items.length;
    items.forEach(function (el, n) { el.classList.toggle("is-active", n === active); });
    items[active].scrollIntoView({ block: "nearest" });
  }

  box.addEventListener("focus", load);
  box.addEventListener("input", function () { load().then(render); });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var items = out.querySelectorAll(".sr-item");
    if (items.length) window.location.href = items[active > -1 ? active : 0].getAttribute("href");
  });
  box.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); setActive(active + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); }
    else if (e.key === "Escape") { box.value = ""; render(); box.blur(); }
  });
  document.addEventListener("click", function (e) { if (!form.contains(e.target)) out.hidden = true; });
  box.addEventListener("focus", function () { if (box.value.trim()) render(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
      e.preventDefault();
      box.focus();
    }
  });
})();
