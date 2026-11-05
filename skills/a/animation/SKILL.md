---
name: animation
description: >-
  Generate real animations and videos entirely from code. Entry point for
  the animation skill: engine stack (Manim video, GSAP, anime.js v4,
  Three.js, Matter.js, Rough.js, CSS keyframes), installation with
  verified versions, engine selection, the seven rules, the shared markup
  contract, one minimal working recipe per engine, a cached video
  pipeline, and how to build an animation system. Detailed, complete
  per-engine documentation lives in the references/ folder
  (manim-video, gsap-timelines, animejs-v4, threejs-3d,
  matterjs-physics, svg-css-baseline). Use for any task that says
  animate, render a video, 3D, physics simulation, motion graphics, or
  set up an animation library.
author: SKT AI LABS
version: 1.0.0
---

# Animation

Install once, pick the right engine per job, follow the rules. Every
recipe here is production-proven on Windows, Node 22, Python 3.14 —
bundled locally, no CDN, works offline.

Versions this skill was verified against:

    Manim Community v0.22.0   Python 3.14.6
    gsap 3.15.0               animejs 4.5.0 (v4 API)
    three 0.186.1             @types/three 0.186
    matter-js 0.20.0          @types/matter-js 0.20.2
    roughjs 4.6.6

## How to use this skill

1. Read THIS file first: it gives you the stack, install steps,
   selection order, the rules, and a minimal recipe per engine.
2. Before writing real code for an engine, open its reference — the
   references contain the FULL implementation: every loop type, every
   cleanup path, every gotcha. Nothing is abbreviated there.

File map:

    skills/animation/
      SKILL.md                    <- you are here: overview + recipes
      references/
        manim-video.md            full video pipeline: templates,
                                  render flags, cache, dedupe
        gsap-timelines.md         draw-on, pops, bars, loops,
                                  svgOrigin, context/revert
        animejs-v4.md             v4 API, eases, keyframes,
                                  loop/alternate, revert
        threejs-3d.md             geometry map, inked edges, lights,
                                  resize, disposal
        matterjs-physics.md       pendulum/freefall/orbit/wave
                                  recipes, teardown order
        svg-css-baseline.md       keyframes, transform origins,
                                  rough.js, kill-switch class
      examples/
        plot_scene.py             runnable install smoke test

## 1. The stack

| Engine | Reach for it when | Install |
|---|---|---|
| Manim (Community) | The deliverable is a VIDEO (mp4): a curve drawing itself, area filling up, one graph morphing into another | `pip install manim` |
| GSAP | The default for any SVG/DOM figure: strokes drawing on, staggered label pops, bars growing from a baseline, infinite loops | `npm i gsap` |
| anime.js v4 | The same jobs with a different easing feel (line-draw, outBack pops, keyframe arrays) | `npm i animejs` |
| Three.js | A real 3D object with depth: cube, cylinder, cone, sphere, a 2D shape extruded into a slab | `npm i three @types/three` |
| Matter.js | Real physics: gravity, pendulums on constraints, bouncing balls, orbits, spring-driven waves | `npm i matter-js @types/matter-js` |
| Rough.js | Hand-drawn whiteboard look — it GENERATES sketchy path data (no motion by itself; CSS/GSAP animate the paths) | `npm i roughjs` |
| CSS keyframes | The zero-JS baseline figure; also the reduced-motion and no-library fallback | none |

Division of labor, stated once:

- Rough.js (and hand-written path math) produce the MARKUP.
- CSS or a JS engine (GSAP / anime.js) animates that markup.
- Matter.js replaces the animation with a real simulation.
- Three.js replaces the SVG entirely with a WebGL canvas.
- Manim replaces the browser with a rendered video file.

## 2. Installation

Node side (bundled locally — never a CDN script tag; frameworks code-split
dynamic imports automatically):

    npm i gsap animejs three matter-js roughjs
    npm i -D @types/three @types/matter-js

`gsap`, `animejs` (v4) and `roughjs` ship their own types; `three` and
`matter-js` need the `@types` packages above.

Verify the Node installs (run from the project root):

    node -e "import('animejs').then(m => console.log(typeof m.animate))"
    -> function        (v4 named export; a default-export means v3)
    node -e "import('gsap').then(m => console.log(typeof m.gsap.timeline))"
    -> function
    node -e "import('three').then(m => console.log(typeof m.Scene))"
    -> function
    node -e "import('matter-js').then(m => console.log(typeof (m.default ?? m).Engine.create))"
    -> function

Video side (bundles imageio-ffmpeg — no system ffmpeg needed, no LaTeX
needed):

    pip install manim
    python -m manim --version     # expect v0.22+

Smoke test (render the example that ships next to this file):

    python -m manim render -ql examples/plot_scene.py MyScene
    # output: media/videos/.../MyScene.mp4 (480p15, a few MB,
    # first render takes ~10s extra for Manim's cold import)

Python interpreter override for odd installs: read it from an env var
(`process.env.PYTHON ?? 'python'` on the Node side).

No TeX on the machine is FINE and by design: every label uses Pango
`Text(...)`, never `Tex`/`MathTex`. A scene that touches LaTeX on a
machine without a TeX distribution dies ~30 seconds into the render.

## 3. Engine selection (apply in this order)

1. **The user asked for a video / mp4** -> Manim. Nothing else renders
   video.
2. **The figure is a solid or has depth** -> Three.js.
3. **The figure is a motion demo and realism matters** (gravity,
   collision, constraint) -> Matter.js.
4. **Any other animated figure** -> GSAP by default; anime.js when a
   second, visibly different flavor is wanted.
5. **Must ship zero JS, or the JS engine failed** -> CSS keyframes. The
   static base state is always the finished pose, so nothing is ever
   blank.

Never: two engines on one figure, a JS engine on a `<video>`, or Manim
for anything interactive.

## 4. The rules

1. **Exactly one animator per element.** If GSAP/anime drives a figure,
   kill the CSS keyframes for it (`animation: none !important` under a
   wrapper class). Two animators fight over `transform` and the figure
   jitters. Query with combined selectors (`'.pop, .dot'`) so each
   element appears in a timeline exactly once.
2. **Draw-on strokes use `pathLength="1"`.** Put `pathLength={1}` on
   every path that should draw itself, then animate
   `stroke-dasharray: 1` + `stroke-dashoffset: 1 -> 0`. Path length is
   then always 1 regardless of geometry — no `getTotalLength()`, no
   drift between renderers.
3. **SVG transforms need an origin you control.** CSS transforms on SVG
   resolve against `transform-box`: use `view-box` + px origins in user
   units (bars grow from the zero line, pendulums swing from their
   pivot) or `fill-box` + `50% 50%` for element-center pops. GSAP
   writes the SVG `transform` attribute instead — hand it the same
   numbers as `svgOrigin: "320 52"`.
4. **Reduced motion = the finished pose, instantly.** Gate every
   animation: CSS inside `@media (prefers-reduced-motion:
   no-preference)`; JS checks
   `matchMedia('(prefers-reduced-motion: reduce)').matches` and skips.
   The base state must already look complete — keyframes animate FROM a
   hidden state, never INTO a visible one.
5. **Every engine cleans up.** GSAP: `gsap.context(fn, root)` then
   `ctx.revert()`. anime.js: collect returned animations, `revert()`
   each. Three.js: cancel rAF, `geometry.dispose()`, `renderer.dispose()`,
   remove canvas, drop resize listeners. Matter.js: `Events.off`,
   `Render.stop`, `Runner.stop`, `Composite.clear`, `Engine.clear`,
   remove canvas (order matters).
6. **Load engines on demand.** `await import('engine')` inside the
   effect, never a top-level import in a shared component. A page with
   no figures never downloads a single animation byte, and the app
   stays offline-safe.
7. **Markup is written once, for the finished state.** The server
   renders static SVG (works with JS off, on first paint, and under
   reduced motion); engines only ADD motion. The engine decision is
   made at parse time so server and client agree — no hydration
   mismatch.

## 5. Shared markup contract

All SVG engines drive the same class vocabulary, so figure code never
changes when the engine does:

| class | on | engines do |
|---|---|---|
| `.draw` | stroke paths (`pathLength=1`) | draw on: dashoffset 1 -> 0 |
| `.fill` | rough/sketch fill paths | fade up |
| `.pop` | labels, dots, value chips | scale + fade in with overshoot |
| `.bar` | `<rect>` bars | grow (scaleY) from baseline origin |
| `.guide`, `.axis`, `.grid`, `.tick`, `.label`, `.title` | chart chrome | fade in first |
| `.swing` | pendulum group | rotate around pivot (view-box origin) |
| `.orbit` | planet group | rotate around center; inline `animationDuration`/`animationDirection` carry per-body speed and direction |
| `.fall` | falling group | translateY bounce loop |
| `.wave` | translated sine group | translateX one period, seamlessly |

Inline styles the markup leaves for any engine (see
`references/svg-css-baseline.md` for the exact CSS):

- `transformBox: 'view-box'` + `transformOrigin: '<px> <px>'` — the
  physical pivot/baseline in user units.
- stagger via `animationDelay` for the CSS path.

The figure wrapper carries the mode:

    <figure className={driven ? 'viz viz-lib' : 'viz'} data-engine={engine}>

- `viz-lib` — CSS keyframes are switched off beneath this class (rule 1).
- `data-engine` — `gsap | anime | three | physics | css | manim` — for
  QA selectors and debugging.

## 6. Recipes (minimal working versions)

Each recipe below is the SMALLEST complete version. The reference file
has the full implementation — all loop types, all cleanup paths, every
gotcha. Read the reference before writing production code.

### CSS (baseline)

    @keyframes draw-k { from { stroke-dashoffset: 1 } to { stroke-dashoffset: 0 } }
    @keyframes pop-k  { from { opacity: 0; transform: scale(0.55) }
                        to   { opacity: 1; transform: scale(1) } }

    .draw { stroke-dasharray: 1; stroke-dashoffset: 0; }  /* finished at rest */

    @media (prefers-reduced-motion: no-preference) {
      .draw { animation: draw-k 0.75s cubic-bezier(0.4, 0, 0.2, 1) both; }
      .pop  { transform-box: fill-box; transform-origin: 50% 50%;
              animation: pop-k 0.38s cubic-bezier(0.2, 0.9, 0.3, 1.35) both; }
    }

Full keyframe set (8 animations), origins, kill-switch, rough.js:
`references/svg-css-baseline.md`.

### GSAP

    const { gsap } = await import('gsap');
    const q = sel => Array.from(root.querySelectorAll(sel));
    const ctx = gsap.context(() => {
      const tl = gsap.timeline();
      const chrome = q('.title, .axis, .label');
      const draws  = q('.draw');
      const pops   = q('.pop, .dot');
      if (chrome.length)
        tl.from(chrome, { opacity: 0, duration: 0.25, stagger: 0.015 }, 0);
      draws.forEach((p, i) => {
        tl.set(p, { strokeDasharray: '1' }, 0);
        tl.fromTo(p, { strokeDashoffset: 1 },
          { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' },
          0.1 + i * 0.08);
      });
      if (pops.length)
        tl.from(pops, { opacity: 0, scale: 0.5, duration: 0.4,
          ease: 'back.out(1.8)', stagger: 0.07 }, '-=0.3');
    }, root);
    // cleanup: return () => ctx.revert();

Bars + all four loops (swing/orbit/fall/wave) + `svgOrigin` handling:
`references/gsap-timelines.md`.

### anime.js v4

    const { animate, set, stagger } = await import('animejs');
    set(paths, { strokeDasharray: '1', strokeDashoffset: 1 });
    const a1 = animate(paths, { strokeDashoffset: 0, duration: 800,
      delay: stagger(90), ease: 'inOutQuad' });
    const a2 = animate(pops, { opacity: [0, 1], scale: [0.5, 1],
      duration: 430, delay: stagger(70), ease: 'outBack' });
    // cleanup: return () => { a1.revert(); a2.revert(); };

Loops, keyframe bounce, eases list, v3-vs-v4 import trap:
`references/animejs-v4.md`.

### Three.js

    const THREE = await import('three');
    const geo = new THREE.BoxGeometry(1.3, 1.3, 1.3);
    const scene = new THREE.Scene();
    scene.add(
      new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: 0xeef2ff, roughness: 0.7, metalness: 0.04, flatShading: true })),
      new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30),
        new THREE.LineBasicMaterial({ color: 0x0f172a })));
    scene.add(new THREE.AmbientLight(0xffffff, 1.0));
    const key = new THREE.DirectionalLight(0xffffff, 1.5);
    key.position.set(3, 5, 4); scene.add(key);
    const camera = new THREE.PerspectiveCamera(38, 16 / 9, 0.1, 60);
    camera.position.set(0, 1.85, 4.7); camera.lookAt(0, 0, 0);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    stageDiv.append(renderer.domElement);
    renderer.render(scene, camera);
    // cleanup: geo.dispose(); renderer.dispose(); renderer.domElement.remove();

Geometry table (every shape + 2D->3D extrusion), resize loop, reduced
motion, WebGL failure ladder: `references/threejs-3d.md`.

### Matter.js

    const mod = await import('matter-js');
    const M = mod.default ?? mod;            // CJS interop — not optional
    const engine = M.Engine.create({ gravity: { x: 0, y: 1, scale: 0.001 } });
    const render = M.Render.create({
      element: mountDiv, engine,
      options: { width: 640, height: 360, background: 'transparent',
                 wireframes: false,
                 pixelRatio: Math.min(2, window.devicePixelRatio) } });
    const runner = M.Runner.create();
    M.Runner.run(runner, engine);
    M.Render.run(render);
    const ground = M.Bodies.rectangle(320, 320, 700, 10, {
      isStatic: true,
      render: { fillStyle: 'rgba(0,0,0,0)', strokeStyle: 'rgba(0,0,0,0)' } });
    const ball = M.Bodies.circle(300, 60, 17, {
      restitution: 0.45, render: { fillStyle: '#0437f2' } });
    M.Composite.add(engine.world, [ground, ball]);
    // cleanup (ORDER MATTERS): Events.off -> Render.stop -> Runner.stop
    //   -> Composite.clear -> Engine.clear -> canvas.remove()

Pendulum / freefall / orbit / spring-wave with exact numbers:
`references/matterjs-physics.md`.

## 7. Video (Manim) — the five rules

1. **Templates, never caller-supplied Python.** A typed spec fills one
   of a few fixed Scene templates. Untrusted input must never become
   code execution.
2. **Validate before rendering.** Compile the expression with the same
   evaluator the on-screen figure uses; if it fails, fall back to the
   static figure instead of burning 30s on a doomed render.
3. **Text, never Tex.** Every label is Pango `Text(...)` — no LaTeX
   dependency, no crash on TeX-less machines.
4. **Cache by content hash + dedupe in-flight.** Same script, same
   video.
5. **Find the output recursively.** Manim's folder naming is not
   stable across versions — walk the tree, never predict the path.

Pipeline flow:

    spec -> validate expr -> fill a Scene template -> sha256(script)
         -> cached? return URL
         -> in flight? await same promise
         -> python -m manim render -ql --format=mp4 scene.py MyScene
         -> find first *.mp4 recursively (150s timeout)
         -> copy to public cache -> <video autoPlay loop muted controls>
         -> on ANY failure: show the static figure (never depend on video)

Full scene templates (plot / area / transform), expression translation
table, spawn arguments, quality flags, error summarizing, player code:
`references/manim-video.md`.

## 8. Building an animation system

The architecture that ties engines into an app:

1. **A figure spec** in plain `key: value` lines, parsed into a typed
   spec: type + geometry keys + one optional `anim:` engine field.
   Streaming-friendly: an unclosed block parses the same as a closed
   one.

    [[viz type=geo]]
    title: Cube — 8 vertices, 6 faces
    shape: cube
    anim: three
    [[/viz]]

2. **An `engineFor(spec)` resolver** — pure and unit-tested:

    export function engineFor(spec: VizSpec): Engine {
      if (spec.type === 'manim' || spec.type === 'unknown') return 'css';
      const want = spec.anim;
      if (want === 'css') return 'css';
      if (want === 'three')   return spec.type === 'geo'    ? 'three'   : 'gsap';
      if (want === 'physics') return spec.type === 'motion' ? 'physics' : 'gsap';
      if (want === 'anime') return 'anime';
      if (want !== '') return 'gsap';                 // a typo still animates
      return spec.type === 'geo' && SOLIDS.includes(spec.shape)
        ? 'three'                                     // solids leap to 3D
        : 'gsap';                                     // default engine
    }

   Asking for an engine that cannot apply (three on a line chart) falls
   back to GSAP rather than failing; a video type is never hijacked; an
   unknown value still gets a library, never silence.

3. **A dispatcher** that renders the static body first (SSR-safe), tags
   the wrapper, mounts a client-only runner:

    const engine = engineFor(spec);
    const body = pickBody(spec, engine);        // three/physics swap the body
    const runner = engine === 'gsap' || engine === 'anime' ? engine : null;
    return (
      <figure ref={root}
              className={runner ? 'viz viz-lib' : 'viz'}
              data-engine={engine} role="img" aria-label={label}>
        {body}
        {runner && <EngineRunner engine={runner} rootRef={root} />}
      </figure>
    );

4. **Runners** (section 6 recipes + the references) that query the
   shared class vocabulary — engines are swappable without touching
   figure code.
5. **A QA page** rendering every engine side by side — one gsap figure,
   one anime, one auto-three solid, one of each physics world, one
   `css` opt-out, one fallback case. SSR HTML alone already proves the
   wiring: count `data-engine="..."`.
6. **A cache layer** for anything expensive: hash the artifact (video),
   an in-flight map for stampedes, the static figure as the universal
   fallback.
7. **Tests that pay for themselves:** resolver matrix (default gsap;
   css opt-out; three/physics validity; solid auto-leap; typo -> gsap;
   manim untouched), spec parsing of `anim:`, and one live page check
   per engine.

## 9. Performance and offline

- Every engine is a dynamic `import()` — a page with no figures
  downloads zero animation bytes; the first figure pays one shared
  chunk, cached thereafter.
- Bundle weights (gzip, approximate): gsap ~70KB, anime ~20KB, matter
  ~90KB, three ~170KB, rough ~15KB. Only Three/Matter carry canvases;
  the SVG engines run on markup already on the page.
- No CDN anywhere — the target machine may be offline; the app does
  not care.
- One timeline per figure, `gsap.context`-scoped; never a global tween
  per element across the document.
- Pause on unmount is mandatory (rAF loops and matter runners
  otherwise run forever in long-lived SPAs).
- Video: the hash cache means re-opening the same figure costs
  nothing; renders are 480p15 unless asked otherwise.

## 10. Troubleshooting

| symptom | cause | fix |
|---|---|---|
| manim dies ~30s in, error mentions TeX | a `Tex`/`MathTex` slipped into a template | `Text(...)` only; no TeX on the machine by design (manim-video.md) |
| manim render "succeeds" but no output found | output folder naming varies by version/stem | walk the temp dir recursively for the first `*.mp4` |
| first manim render very slow | cold Python + Manim import (~10s) | expected; 150s timeout, hash cache makes it once-per-figure |
| `animate is not a function` | anime v3 default import on a v4 install | `const { animate } = await import('animejs')` |
| matter bodies fall to one corner / import empty | UMD namespace not unwrapped | `const M = mod.default ?? mod` |
| three: "Could not find a declaration file" | types not installed | `npm i -D @types/three` |
| `new WebGLRenderer` throws | blocked/absent WebGL | try/catch -> flat 2D fallback |
| figure jitters or moves twice | CSS keyframes AND a JS engine both running | kill CSS under the engine wrapper class (rule 1) |
| figure invisible under reduced motion | base state was the hidden start | base = finished pose; keyframes animate FROM hidden (rule 4) |
| bar grows from the chart corner, not the baseline | missing transform origin | inline `transform-box: view-box` + px origin (rule 3) |
| pendulum spins around the wrong point in GSAP | `svgOrigin` missing | read the inline `transformOrigin`, strip `px` |
| video autoplays then pauses in an embedded webview | strict autoplay policy | keep `muted` + `controls`; playback via controls always works |
| doubled canvases / doubled worlds in dev | React StrictMode double effect | full teardown (references) makes the second run clean |
| figure blank right after hydration | `from()` start states + missing CSS kill | ship the kill class in the FIRST paint (decide it at parse time) |

## 11. Quick reference card

    pick:   video -> Manim | solid -> Three | physics -> Matter
            other -> GSAP (alt: anime.js) | zero-JS -> CSS
    draw:   pathLength="1" + dasharray 1 + dashoffset 1 -> 0
    origin: CSS transform-box view-box + px | GSAP svgOrigin "x y"
    reduce: matchMedia check -> skip engine; CSS inside no-preference
    load:   await import('engine') in the effect, never top-level
    unmount: ctx.revert() | anims.revert() | dispose+remove | Events.off,
             Render.stop, Runner.stop, Composite.clear, Engine.clear
    video:  templates only, Text not Tex, validate expr first,
            python -m manim render -ql --format=mp4, 150s timeout,
            recursive mp4 find, sha256[:24] cache, in-flight dedupe,
            <video autoPlay loop muted controls>, static fallback
    qa:     one QA page, count data-engine, one figure per engine

Runnable smoke test for the video half lives next to this file:

    python -m manim render -ql examples/plot_scene.py MyScene
