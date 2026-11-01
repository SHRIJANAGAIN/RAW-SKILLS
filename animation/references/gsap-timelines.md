# GSAP timelines — full reference

GSAP is the default JS engine for SVG/DOM figures. One timeline per
figure, built after mount, scoped to the figure root, destroyed with
one `ctx.revert()`.

Contents:
1. Loading (dynamic import + async guard)
2. Query helpers and the standard class groups
3. The complete figure timeline (chrome -> draw -> pops -> bars)
4. The four loops: swing, orbit, fall, wave
5. `svgOrigin` — why GSAP needs it
6. Cleanup with `gsap.context`
7. Gotchas

---

## 1. Loading

Never import gsap at module top level in a shared component — that
puts it in the entry bundle for pages with no figures. Import inside
the effect:

```js
const { gsap } = await import('gsap');   // ~70KB gzip, code-split
```

The import is async, so the effect must guard against unmount while
the chunk is in flight:

```jsx
useEffect(() => {
  const root = rootRef.current;
  if (root === null) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  let dead = false;
  let stop;
  runGsap(root).then(kill => {
    if (dead) kill();          // unmounted during import: revert now
    else stop = kill;          // normal: keep the cleanup handle
  });
  return () => {
    dead = true;
    stop?.();                  // already running: revert
  };
}, [rootRef]);
```

Why the `dead` flag: without it, a fast unmount leaks a running
timeline (the `.then` fires after cleanup and nobody holds the kill
handle). Both paths must end in `ctx.revert()`.

## 2. Query helpers and class groups

```js
const q = sel => Array.from(root.querySelectorAll(sel));

const draws   = q('.draw');      // pathLength=1 stroke paths
const fills   = q('.fill');      // rough/sketch fill paths
const pops    = q('.pop, .dot'); // labels + dots, ONE pass each
const bars    = q('.bar');       // <rect> bars
const chrome  = q('.title, .axis, .grid, .tick, .label, .guide, .orbit-line');
const swings  = q('.swing');
const orbits  = q('.orbit');
const falls   = q('.fall');
const waves   = q('.wave');
```

Combined selectors are mandatory where classes overlap (`.pop, .dot`):
if an element matched two separate queries it would enter the timeline
twice and animate twice — the visual result is jitter.

## 3. The complete figure timeline

```js
async function runGsap(root) {
  const { gsap } = await import('gsap');

  /* ...the q(...) queries from section 2... */

  // "320px 52px" (the view-box origin the CSS left behind) -> "320 52"
  const originOf = el => el.style.transformOrigin.replace(/px/g, '').trim();

  const ctx = gsap.context(() => {
    const tl = gsap.timeline();

    // (1) chrome fades in first — the frame before the content
    if (chrome.length) {
      tl.from(chrome, { opacity: 0, duration: 0.25, stagger: 0.015 }, 0);
    }

    // (2) strokes draw on — pathLength=1 means dasharray is just "1"
    draws.forEach((p, i) => {
      tl.set(p, { strokeDasharray: '1' }, 0);
      tl.fromTo(
        p,
        { strokeDashoffset: 1 },
        { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' },
        0.1 + i * 0.08,
      );
    });

    // (3) fills (sketch shading), then labels pop with overshoot
    if (fills.length) {
      tl.from(fills, { opacity: 0, duration: 0.35, stagger: 0.04 }, 0.3);
    }
    if (pops.length) {
      tl.from(
        pops,
        { opacity: 0, scale: 0.5, duration: 0.4,
          ease: 'back.out(1.8)', stagger: 0.07 },
        '-=0.3',
      );
    }

    // (4) bars grow out of the baseline (see section 5 for svgOrigin)
    bars.forEach((bar, i) => {
      const org = originOf(bar);
      tl.from(
        bar,
        { scaleY: 0,
          ...(org === '' ? {} : { svgOrigin: org }),
          duration: 0.5, ease: 'power3.out' },
        0.3 + i * 0.09,
      );
    });

    /* ...the four loops from section 4... */
  }, root);

  return () => ctx.revert();
}
```

Phase design notes:

- Positions are absolute seconds from timeline start; `'-=0.3'` means
  "0.3s before the previous tween ended" — that overlap is what makes
  pops feel connected to the draw instead of queued after it.
- `from()`/`fromTo()` capture the start state IMMEDIATELY when the
  tween is created. With CSS killed (`viz-lib`) and the base state
  finished, there is no visible flash before the motion begins.
- `set(..., 0)` at position 0 forces `strokeDasharray` before anything
  renders, so a partially-drawn stroke never appears un-dashed.

## 4. The four loops

All four are created INSIDE the same `gsap.context` callback — one
`ctx.revert()` then kills every looping timeline, including nested
ones. No per-tween bookkeeping.

### Swing (pendulum, alternate yoyo)

```js
for (const s of swings) {
  const org = originOf(s);            // pivot: "320 52"
  tl.fromTo(
    s,
    { rotation: -24 },
    { rotation: 24,
      ...(org === '' ? {} : { svgOrigin: org }),
      duration: 1.05, yoyo: true, repeat: -1, ease: 'sine.inOut' },
  );
}
```

`yoyo: true` + `repeat: -1` plays forward then backward forever —
an alternate loop identical to the CSS `alternate` keyword. Match the
CSS angles (-24/24) or the two engines look different.

### Orbit (per-body speed from inline CSS)

```js
for (const o of orbits) {
  const dur = Number.parseFloat(o.style.animationDuration) || 7;
  const org = originOf(o);            // center: "320 210"
  tl.to(
    o,
    { rotation: o.style.animationDirection === 'reverse' ? -360 : 360,
      ...(org === '' ? {} : { svgOrigin: org }),
      duration: dur, ease: 'none', repeat: -1 },
    0,
  );
}
```

- A full 360 turn loops with no seam; any other end angle jumps.
- The markup wrote `animationDuration`/`animationDirection` inline for
  the CSS path — GSAP reads them back, so per-body speeds survive the
  engine swap.
- `ease: 'none'` = constant angular speed (orbits do not ease).

### Fall (drop + two decaying bounces)

```js
for (const f of falls) {
  const ft = gsap.timeline({ repeat: -1, repeatDelay: 0.4 });
  ft.to(f, { y: 205, duration: 0.75, ease: 'power2.in' })    // fall
    .to(f, { y: 159, duration: 0.3,  ease: 'power1.out' })   // bounce 1
    .to(f, { y: 205, duration: 0.26, ease: 'power1.in' })
    .to(f, { y: 191, duration: 0.16, ease: 'power1.out' })   // bounce 2
    .to(f, { y: 205, duration: 0.12, ease: 'power1.in' })
    .to(f, { opacity: 0, duration: 0.25 })                   // hide teleport
    .set(f, { y: 0, opacity: 0 })                            // reset offscreen
    .to(f, { opacity: 1, duration: 0.3 });                   // reappear
  tl.add(ft, 0);
}
```

The fade-out/fade-in around the reset hides the instant jump back to
the top — without it the ball teleports visibly. `repeatDelay: 0.4`
gives a beat at the bottom so it reads as repeated drops.

### Wave (seamless translate)

```js
for (const w of waves) {
  tl.to(w, { x: -320, duration: 3.4, ease: 'none', repeat: -1 }, 0);
}
```

`-320` must equal ONE period of the drawn sine, and the path must
extend at least one extra period past the visible edge on both sides —
otherwise the loop point shows a seam. `ease: 'none'` keeps the wave
speed constant.

## 5. `svgOrigin` — why GSAP needs it

GSAP writes the SVG `transform` ATTRIBUTE (`transform="rotate(...)"`),
not CSS. SVG attribute transforms always resolve around the SVG user
space origin (top-left 0,0) unless a `transform-origin` attribute is
present — and CSS `transform-box` does not apply to the attribute
path. So rotation around a pivot needs `svgOrigin` with explicit user
units:

```js
// WRONG: cube spins around the chart corner
tl.to(el, { rotation: 360, repeat: -1 });

// RIGHT: spins around its own center at (320, 210)
tl.to(el, { rotation: 360, svgOrigin: '320 210', repeat: -1 });
```

The markup already carries the right numbers in inline CSS (for the
CSS path), so read them back rather than hard-coding a second copy:

```js
const originOf = el => el.style.transformOrigin.replace(/px/g, '').trim();
// "320px 52px" -> "320 52"   (svgOrigin takes space-separated units)
```

If the inline style is empty (an element without an origin), omit
`svgOrigin` entirely — spreading `{}` — rather than passing an empty
string, which GSAP rejects.

Note: GSAP's inline-written SVG transform attribute does NOT
interfere with the CSS `transform-box`/`transform-origin` the CSS path
uses — the two mechanisms never run on the same element at the same
time (kill-switch rule), and the attribute simply wins when present.

## 6. Cleanup with `gsap.context`

```js
const ctx = gsap.context(() => { /* timeline construction */ }, root);
return () => ctx.revert();
```

What `revert()` does:

- Kills every tween and timeline created inside the callback —
  including nested loops, `repeat: -1` timelines, and deferred
  `.add()`ed children.
- Restores inline styles/GSAP-set attributes to their pre-tween
  values, so a remount starts from the clean static markup.

Scope matters: pass `root` as the second argument and gsap records
creation against that element (also enabling scoped selector strings).
A context created on `document` would leak tweens across figures.

In React StrictMode (double-invoked effects) `revert()` makes the
second run start clean — if you see doubled motion in dev, your cleanup
is not reaching the context.

## 7. Gotchas

- **Two animators, one element.** If `viz-lib` is missing from the
  wrapper, CSS keyframes and gsap fight over `transform` — the figure
  jitters. Decide the class at parse time so the first paint already
  has it.
- **Wrong rotation center** = missing `svgOrigin` (section 5).
- **`from()` flash** = the element was visible, then jumped to the
  start state. Fixed automatically when base state = finished pose
  (CSS baseline rule).
- **Combined selectors** — query each element exactly once
  (`'.pop, .dot'` in ONE query, not two).
- **Async import leak** — the `dead`/`stop` guard from section 1 is
  not optional.
- **`repeat: -1` never stops by itself** — only `ctx.revert()` does.
  Never attach a bare `gsap.to(...)` loop outside a context.
- **Rotation deltas**: full turns (360) loop seamlessly; animating
  `+=360` on an element that also has CSS rotation drifts — the
  engines are exclusive, so pick one.
