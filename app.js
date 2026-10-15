/* Nyakarilo deck — slide viewer, link copying and social sharing. */
(function () {
  "use strict";

  var PAGES = 10;
  var TITLE = "Nyakarilo Agro-Tourism & Farmhouse Retreat — Investor Pitch Deck";
  var BLURB =
    "Premier hospitality and an organic farm-to-table experience in Rwamagana, Rwanda. " +
    "4,000 sqm boutique eco-retreat · 100,000,000 RWF fully costed capital plan.";

  function pageUrl(n) {
    var base = location.href.split("#")[0];
    return n ? base + "#slide-" + n : base;
  }
  function image(n) {
    return "pages/page-" + (n < 10 ? "0" + n : n) + ".png";
  }

  /* ---------- slide viewer ---------- */
  var box = document.getElementById("lightbox");
  var img = document.getElementById("lb-img");
  var count = document.getElementById("lb-count");
  var current = 0;
  var lastFocus = null;

  function show(n) {
    if (n < 1) n = PAGES;
    if (n > PAGES) n = 1;
    current = n;
    img.src = image(n);
    img.alt = "Slide " + n + " of " + PAGES;
    count.textContent = "Slide " + n + " of " + PAGES;
    if (box.hidden) {
      lastFocus = document.activeElement;
      box.hidden = false;
      document.body.style.overflow = "hidden";
      history.replaceState(null, "", "#slide-" + n);
    }
  }
  function close() {
    if (box.hidden) return;
    box.hidden = true;
    img.removeAttribute("src");
    document.body.style.overflow = "";
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  Array.prototype.forEach.call(document.querySelectorAll(".deck button"), function (b) {
    b.addEventListener("click", function () {
      show(parseInt(b.getAttribute("data-page"), 10));
    });
  });
  document.getElementById("lb-close").addEventListener("click", close);
  document.getElementById("lb-prev").addEventListener("click", function () { show(current - 1); });
  document.getElementById("lb-next").addEventListener("click", function () { show(current + 1); });
  box.addEventListener("click", function (e) { if (e.target === box) close(); });
  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(current - 1);
    if (e.key === "ArrowRight") show(current + 1);
  });

  /* ---------- copy the link ---------- */
  var hints = [document.getElementById("copy-hint"), document.getElementById("copy-hint-2")]
    .filter(Boolean);
  var hintTimer = null;
  function flash(message) {
    hints.forEach(function (el) { el.textContent = message; });
    if (hintTimer) clearTimeout(hintTimer);
    hintTimer = setTimeout(function () {
      hints.forEach(function (el) { el.textContent = ""; });
    }, 4000);
  }
  function copyLink() {
    var url = pageUrl(0);
    var done = function () { flash("Link copied — paste it into your social media post."); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, function () { fallbackCopy(url); });
    } else {
      fallbackCopy(url);
    }
  }
  ["copy-link", "copy-link-2"].forEach(function (id) {
    var btn = document.getElementById(id);
    if (btn) btn.addEventListener("click", copyLink);
  });
  function fallbackCopy(text) {
    var t = document.createElement("textarea");
    t.value = text;
    t.setAttribute("readonly", "");
    t.style.position = "fixed";
    t.style.opacity = "0";
    document.body.appendChild(t);
    t.select();
    try { document.execCommand("copy"); flash("Link copied — paste it into your social media post."); }
    catch (err) { flash("Copy this link: " + text); }
    document.body.removeChild(t);
  }

  /* ---------- share targets ---------- */
  var url = pageUrl(0);
  var encoded = encodeURIComponent(url);
  var text = encodeURIComponent(TITLE + "\n" + BLURB);
  var targets = {
    whatsapp: "https://wa.me/?text=" + text + "%0A" + encoded,
    facebook: "https://www.facebook.com/sharer/sharer.php?u=" + encoded,
    linkedin: "https://www.linkedin.com/sharing/share-offsite/?url=" + encoded,
    x: "https://twitter.com/intent/tweet?text=" + text + "&url=" + encoded,
    email: "mailto:?subject=" + encodeURIComponent(TITLE) + "&body=" + text + "%0A%0A" + encoded
  };
  Array.prototype.forEach.call(document.querySelectorAll("[data-share]"), function (a) {
    var key = a.getAttribute("data-share");
    if (!targets[key]) return;
    a.href = targets[key];
    if (key !== "email") { a.target = "_blank"; a.rel = "noopener noreferrer"; }
  });

  /* show whichever domain the page is served from on the preview card */
  var site = document.getElementById("card-site");
  if (site && location.hostname) site.textContent = location.hostname;

  document.getElementById("year").textContent = String(new Date().getFullYear());

  /* deep link straight to a slide: site/#slide-7 */
  var m = /^#slide-(\d+)$/.exec(location.hash);
  if (m) show(parseInt(m[1], 10));
})();
