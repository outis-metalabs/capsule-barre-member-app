/* Hana renderer: one place that decides how Hana is drawn.
   - Only when HANA_RIV is true (committed switch) and assets/hana/hana.riv exists (one HEAD check), the Rive runtime is loaded lazily
     from a CDN and a canvas replaces the WebP figure inside the existing Hana stage (.hw box), driven by
     the brief's state machine HanaSM: number input `moment`, triggers tap / success / error / talk.
   - Otherwise nothing else is fetched and the WebP loops / stills keep working exactly as before.
   - Reduced motion never loads Rive: the member sees the stills (same as today). */
(function () {
  "use strict";
  /* App moment (hanaState / todayMoment / Ask reply pose) -> brief moment number. The only mapping table. */
  const MOMENT = { front: 0, greet: 1, book: 2, nobook: 3, sleep: 4, warmup: 5, cheer: 6,
                   calm: 7, cleared: 8, paused: 9, low: 10, wink: 11, thinking: 12 };
  /* Committed switch: set to true in the same commit that adds assets/hana/hana.riv.
     While false nothing is probed or fetched (no HEAD request, no 404 in the console). ?rive=1 forces a check for testing. */
  const HANA_RIV = false;
  const RIV = "assets/hana/hana.riv";
  const CDN = "https://cdn.jsdelivr.net/npm/@rive-app/canvas@2.44.2/rive.js";
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches || !!window.__hanaStill;
  let status = "idle";          /* idle -> checking -> loading -> ready | off */
  let r = null, canvas = null, inputs = {}, lastMoment = null, pending = [];

  function momentOf(st) { return MOMENT[st] != null ? MOMENT[st] : 0; }
  function input(n) { return inputs[n] || null; }
  function setMoment(st) { const i = input("moment"); const v = momentOf(st); if (i && lastMoment !== v) { i.value = v; lastMoment = v; } }
  function fire(n) {
    if (status !== "ready" || reduced()) return false;
    const i = input(n); if (i && i.fire) { i.fire(); return true; } return false;
  }
  function stage() { return document.querySelector(".hana-stage .hw[data-hana], .hero .hw[data-hana]"); }

  function mount() {
    if (status !== "ready") return;
    const h = stage();
    document.querySelectorAll(".hw.rive").forEach(el => { if (el !== h) el.classList.remove("rive"); });
    if (!h || reduced()) { if (canvas) canvas.remove(); return; }
    if (canvas.parentNode !== h) h.appendChild(canvas);
    h.classList.add("rive");
    const w = h.clientWidth, ht = h.clientHeight, dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(ht * dpr)) {
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(ht * dpr);
      try { r.resizeDrawingSurfaceToCanvas(); } catch (e) {}
    }
    setMoment(h.dataset.s);
  }

  function boot() {
    const s = document.createElement("script");
    s.src = CDN; s.async = true; s.crossOrigin = "anonymous";
    s.onerror = () => { status = "off"; };
    s.onload = () => {
      try {
        const rive = window.rive; if (!rive) { status = "off"; return; }
        canvas = document.createElement("canvas"); canvas.className = "hana-rive"; canvas.setAttribute("aria-hidden", "true");
        r = new rive.Rive({
          src: RIV, canvas, artboard: "Hana", stateMachines: "HanaSM", autoplay: true,
          layout: new rive.Layout({ fit: rive.Fit.Contain, alignment: rive.Alignment.BottomCenter }),
          onLoad: () => {
            (r.stateMachineInputs("HanaSM") || []).forEach(i => { inputs[i.name] = i; });
            if (!inputs.moment) { status = "off"; try { r.cleanup(); } catch (e) {} return; }
            status = "ready"; mount(); pending.splice(0).forEach(fire);
          },
          onLoadError: () => { status = "off"; }
        });
      } catch (e) { status = "off"; }
    };
    document.head.appendChild(s);
  }

  function check() {
    if (status !== "idle") return;
    if (!(HANA_RIV || /[?&]rive=1\b/.test(location.search))) { status = "off"; return; }
    if (reduced() || !window.fetch || /[?&]rive=0\b/.test(location.search)) return;
    status = "checking";
    fetch(RIV, { method: "HEAD", cache: "no-store" })
      .then(res => { if (res.ok) { status = "loading"; boot(); } else status = "off"; })
      .catch(() => { status = "off"; });
  }

  window.HanaRenderer = {
    MOMENT, momentOf, HANA_RIV,
    get active() { return status === "ready" && !reduced(); },
    get status() { return status; },
    /* call after every render */
    sync() { if (status === "idle") check(); else mount(); },
    tap() { return fire("tap"); },
    success() { if (status === "loading" || status === "checking") pending.push("success"); return fire("success"); },
    error() { return fire("error"); },
    talk() { return fire("talk"); }
  };
})();
