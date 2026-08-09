/* The blueprint that assembles itself.
 *
 * A scroll-scrubbed scene showing what OAB does when it helps design a system: a vague brief
 * resolves into measured numbers, a complexity budget locks, a proportional architecture draws
 * itself as an isometric cube — and the components the numbers do NOT justify stay ghosted beside
 * it, each labelled with the measurement that would summon it. You watch it refuse to over-build.
 *
 * GSAP + ScrollTrigger are vendored in vendor/ (no external request at runtime — the site's own
 * principle). Pinning is CSS position:sticky; ScrollTrigger only scrubs the timeline, which is the
 * robust pattern that avoids pin-induced layout jumps.
 *
 * Quality floor, honoured even in the kinetic direction:
 *   - prefers-reduced-motion: no scrub, no scrub-jacking — the final composed state is rendered
 *     statically and the tall scroll track collapses.
 *   - The scene is fully legible without JS: markup ships in its end state, and this script sets
 *     the initial (pre-animation) state itself, so a script failure leaves everything visible.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-blueprint]");
  if (!root || !window.gsap || !window.ScrollTrigger) return; // graceful: HTML stays in end state

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return; // markup is already the composed end state; leave it

  gsap.registerPlugin(ScrollTrigger);

  // reserve the tall scroll track only now that we know the scrubbed version will run
  var track = root.querySelector(".bp-track");
  if (track) track.classList.add("is-live");

  var q = function (s) { return root.querySelector(s); };
  var qa = function (s) { return Array.prototype.slice.call(root.querySelectorAll(s)); };

  // --- set the pre-animation state (the HTML ships composed; we wind it back) ----------------
  var brief = q(".bp-brief");
  var numbers = qa(".bp-metric");
  var gate = q(".bp-gate-fill");
  var gateLabel = q(".bp-gate .bp-gate-value");
  var cubePaths = qa(".bp-cube [data-draw]");
  var cubeAccents = qa(".bp-cube [data-accent]");
  var built = qa(".bp-built li");
  var rejects = qa(".bp-reject");
  var steps = qa(".bp-step");
  var caption = q(".bp-caption");

  gsap.set(brief, { opacity: 0.35, filter: "blur(6px)", letterSpacing: "0.12em" });
  gsap.set(numbers, { opacity: 0, y: 12 });
  gsap.set(gate, { scaleX: 0, transformOrigin: "left center" });
  cubePaths.forEach(function (p) {
    var len = p.getTotalLength();
    gsap.set(p, { strokeDasharray: len, strokeDashoffset: len, opacity: 1 });
  });
  gsap.set(cubeAccents, { opacity: 0, scale: 0, transformOrigin: "center" });
  gsap.set(built, { opacity: 0, x: -14 });
  gsap.set(rejects, { opacity: 0, x: 14 });
  gsap.set(caption, { opacity: 0, y: 10 });

  // Blocks that only arrive at the end must not reserve their height from the start, or the
  // scene is a mostly-empty panel for two thirds of the scroll. Collapse them to zero height and
  // let GSAP animate back to auto when the refuse phase begins.
  var rejectsBlock = q(".bp-rejects");
  var lateBlocks = [rejectsBlock, caption].filter(Boolean);
  gsap.set(lateBlocks, { height: 0, marginTop: 0, paddingTop: 0, borderTopWidth: 0 });

  // Counters must be TWEENS IN THE TIMELINE, not tweens fired from a callback. A tween created
  // inside .add(fn) runs on its own clock: it plays once, ignores the scrub, and never reverses
  // when you scroll back — so the number simply appears at its final value. Returning the tween
  // and adding it to the timeline is what makes it count with the scroll, both ways.
  function counterTween(el) {
    var end = parseFloat(el.getAttribute("data-to"));
    var dp = parseInt(el.getAttribute("data-dp") || "0", 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var obj = { v: 0 };
    return gsap.to(obj, {
      v: end, duration: 0.55, ease: "power1.out",
      onUpdate: function () { el.textContent = obj.v.toFixed(dp) + suffix; }
    });
  }

  function activateStep(i) {
    steps.forEach(function (s, j) { s.classList.toggle("is-active", j === i); });
  }

  // --- the timeline, scrubbed by scroll ------------------------------------------------------
  // Trigger on the TRACK, not the whole section: the track is exactly the span over which the
  // stage is stuck, so the timeline maps 1:1 to the pinned duration. Triggering on the section
  // (which includes the intro block) burned the first ~17% of the timeline before the scene was
  // ever pinned, so the brief resolved off-screen.
  var tl = gsap.timeline({
    scrollTrigger: {
      trigger: track || root,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.6
    }
  });

  // FRAME → QUANTIFY: the vague brief resolves, numbers appear and count up with the scroll
  tl.add(function () { activateStep(0); })
    .to(brief, { opacity: 1, filter: "blur(0px)", letterSpacing: "0em", duration: 0.5 })
    .add(function () { activateStep(1); })
    .to(numbers, { opacity: 1, y: 0, duration: 0.4, stagger: 0.12 }, "quant");
  numbers.forEach(function (el, i) {
    tl.add(counterTween(el), "quant+=" + (i * 0.12));
  });

  // BUDGET: the gate fills and locks
  tl.add(function () { activateStep(2); })
    .to(gate, { scaleX: 1, duration: 0.5, ease: "power2.inOut" })
    .add(function () { if (gateLabel) gateLabel.classList.add("is-locked"); });

  // BUILD: the isometric cube draws itself, components label in
  tl.add(function () { activateStep(3); })
    .to(cubePaths, { strokeDashoffset: 0, duration: 0.85, stagger: 0.1, ease: "power1.inOut" }, "build")
    .to(cubeAccents, { opacity: 1, scale: 1, duration: 0.35, stagger: 0.12 }, "build+=0.75")
    .to(built, { opacity: 1, x: 0, duration: 0.35, stagger: 0.12 }, "build+=0.55");

  // REFUSE: the rejected components ghost in with their triggers; the caption lands
  tl.add(function () { activateStep(4); })
    .to(lateBlocks, { height: "auto", marginTop: "", paddingTop: "", borderTopWidth: "",
                      duration: 0.45, ease: "power2.out" }, "refuse")
    .to(rejects, { opacity: 1, x: 0, duration: 0.4, stagger: 0.12 }, "refuse+=0.15")
    .to(caption, { opacity: 1, y: 0, duration: 0.5 }, "refuse+=0.5");

  // keep ScrollTrigger honest if fonts/images shift layout after load
  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
})();
