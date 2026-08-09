/* The same brief, two answers.
 *
 * A scroll-scrubbed contrast, because the value of OAB is invisible until you see the two answers
 * side by side — that is risk P1 in docs/design/07-roadmap-and-risks.md, and this section is its
 * prescribed fix. The left panel is the developer's dread made visible: a stack that piles up fast
 * while counters climb past a budget nobody checked. The right is the measured answer, with the
 * refusals and the number that would reverse each one.
 *
 * The pain has to land before the resolution, so the timeline holds on the left panel before
 * answering it.
 *
 * GSAP + ScrollTrigger are vendored in vendor/ (no external request at runtime). The stage pins
 * with CSS sticky; ScrollTrigger only scrubs, which avoids pin-induced layout jumps.
 *
 * Quality floor: the markup ships in its composed end state and this script winds it back, so no
 * JS or prefers-reduced-motion leaves the whole comparison readable and compact.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-blueprint]");
  if (!root || !window.gsap || !window.ScrollTrigger) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  gsap.registerPlugin(ScrollTrigger);

  var track = root.querySelector(".bp-track");
  if (track) track.classList.add("is-live");

  var q = function (s) { return root.querySelector(s); };
  var qa = function (s) { return Array.prototype.slice.call(root.querySelectorAll(s)); };

  var brief = q(".bp-brief");
  var bloat = q(".bp-panel-bloat");
  var oab = q(".bp-panel-oab");
  var stack = qa(".bp-stack li");
  var built = qa(".bp-built li");
  var fact = q(".bp-fact");
  var rejects = qa(".bp-reject");
  var caption = q(".bp-caption");
  var counts = qa(".bp-count");

  var bloatMeters = q(".bp-panel-bloat .bp-meters");
  var punch = q(".bp-punch");
  var oabMeters = q(".bp-panel-oab .bp-meters");
  var rejectBlock = q(".bp-rejects");

  // --- wind the composed markup back to its start ------------------------------------------
  gsap.set(brief, { opacity: 0, y: 10 });
  gsap.set([bloat, oab], { opacity: 0 });
  gsap.set(stack, { opacity: 0, y: -8 });
  gsap.set(built, { opacity: 0, x: -10 });
  gsap.set(fact, { opacity: 0 });
  gsap.set(rejects, { opacity: 0, x: 10 });

  // Blocks that arrive late collapse to nothing, so each panel is sized by what is visible rather
  // than by its final content — otherwise both are mostly empty box for half the scroll.
  var late = [bloatMeters, punch, oabMeters, rejectBlock, caption].filter(Boolean);
  gsap.set(late, { height: 0, marginTop: 0, paddingTop: 0, borderTopWidth: 0 });

  // Counters are tweens IN the timeline. Created inside a callback they run on their own clock:
  // they fire once, ignore the scrub and never reverse, so the number just appears at its end
  // value. That bug shipped once already.
  function counterTween(el) {
    var end = parseFloat(el.getAttribute("data-to"));
    var dp = parseInt(el.getAttribute("data-dp") || "0", 10);
    var prefix = el.getAttribute("data-prefix") || "";
    var obj = { v: 0 };
    return gsap.to(obj, {
      v: end, duration: 0.5, ease: "power1.out",
      onUpdate: function () {
        var n = obj.v.toFixed(dp);
        if (dp === 0) n = Number(n).toLocaleString("en-GB");
        el.textContent = prefix + n;
      }
    });
  }
  counts.forEach(function (el) { el.textContent = (el.getAttribute("data-prefix") || "") + "0"; });

  var tl = gsap.timeline({
    scrollTrigger: { trigger: track || root, start: "top top", end: "bottom bottom", scrub: 0.6 }
  });

  // 1 — the brief, stated once
  tl.to(brief, { opacity: 1, y: 0, duration: 0.4 });

  // 2 — THE PAIN. The stack piles up; the counters climb past a budget nobody checked.
  tl.to(bloat, { opacity: 1, duration: 0.3 }, "pain")
    .to(stack, { opacity: 1, y: 0, duration: 0.22, stagger: 0.11 }, "pain+=0.15")
    .to(bloatMeters, { height: "auto", marginTop: "", duration: 0.3 }, "pain+=0.95");
  qa(".bp-panel-bloat .bp-count").forEach(function (el, i) {
    tl.add(counterTween(el), "pain+=" + (1.0 + i * 0.15));
  });
  tl.to(punch, { height: "auto", paddingTop: "", borderTopWidth: "", duration: 0.3 }, "pain+=1.5");

  // hold on the pain before answering it — the dread needs a beat to land
  tl.to({}, { duration: 0.5 });

  // 3 — the measured answer
  tl.to(oab, { opacity: 1, duration: 0.35 }, "answer")
    .to(fact, { opacity: 1, duration: 0.3 }, "answer+=0.1");
  qa(".bp-panel-oab .bp-fact .bp-count").forEach(function (el) {
    tl.add(counterTween(el), "answer+=0.15");
  });
  tl.to(built, { opacity: 1, x: 0, duration: 0.25, stagger: 0.1 }, "answer+=0.4")
    .to(oabMeters, { height: "auto", marginTop: "", duration: 0.3 }, "answer+=0.85");
  qa(".bp-panel-oab .bp-meters .bp-count").forEach(function (el, i) {
    tl.add(counterTween(el), "answer+=" + (0.9 + i * 0.15));
  });

  // 4 — the refusals, each with the number that would reverse it
  tl.to(rejectBlock, { height: "auto", paddingTop: "", borderTopWidth: "", duration: 0.3 }, "refuse")
    .to(rejects, { opacity: 1, x: 0, duration: 0.25, stagger: 0.12 }, "refuse+=0.15")
    .to(caption, { height: "auto", marginTop: "", duration: 0.4 }, "refuse+=0.6");

  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
})();
