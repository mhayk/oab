/* Scroll reveal for the narrative sections. Vanilla, ~0.5KB, no dependency — GSAP is reserved
 * for the one scrubbed section that genuinely needs a timeline.
 *
 * The class is added by JS so that with scripting disabled every section is simply visible;
 * prefers-reduced-motion is honoured in CSS rather than here, so the sections still reveal
 * their content without moving. */
(function () {
  "use strict";
  var els = document.querySelectorAll(".reveal");
  if (!els.length || !("IntersectionObserver" in window)) return;
  document.documentElement.classList.add("js-reveal");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -12% 0px", threshold: 0.05 });
  els.forEach(function (el) { io.observe(el); });
})();
