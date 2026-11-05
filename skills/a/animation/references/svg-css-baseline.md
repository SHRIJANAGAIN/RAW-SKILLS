# SVG + CSS baseline — the zero-JS layer

This is the foundation every other engine replaces. It needs no
JavaScript, no bundler, no install. If a JS engine fails, this is the
fallback. If reduced motion is on, this is what shows — as a finished
still figure.

Contents:
1. The eight keyframes
2. How to apply them (media query + finished base state)
3. Stagger and per-element timing
4. Transform origins on SVG (view-box vs fill-box)
5. The engine kill-switch class
6. Rough.js — sketchy geometry generation
7. When CSS alone is the right choice

---

## 1. The eight keyframes

Eight animations cover every figure type in this skill:

```css
@keyframes draw-k {                       /* stroke drawing itself on */
  from { stroke-dashoffset: 1 }
  to   { stroke-dashoffset: 0 }
}

@keyframes fade-k { from { opacity: 0 } to { opacity: 1 } }

@keyframes pop-k {                        /* labels, dots, value chips */
  from { opacity: 0; transform: scale(0.55) }
  to   { opacity: 1; transform: scale(1) }
}

@keyframes grow-k {                       /* bars from a baseline */
  from { transform: scaleY(0) }
  to   { transform: scaleY(1) }
}

@keyframes swing-k {                      /* pendulum, alternate loop */
  from { transform: rotate(-24deg) }
  to   { transform: rotate(24deg) }
}

@keyframes orbit-k {                      /* full turn, seamless loop */
  from { transform: rotate(0deg) }
  to   { transform: rotate(360deg) }
}

@keyframes fall-k {                       /* drop + two decaying bounces */
  0%   { transform: translateY(0) }
  60%  { transform: translateY(205px) }   /* hit the ground */
  75%  { transform: translateY(159px) }   /* bounce 1 (46px) */
  85%  { transform: translateY(205px) }   /* land */
  90%  { transform: translateY(191px) }   /* bounce 2 (14px) */
  100% { transform: translateY(205px) }   /* final rest */
}

@keyframes wave-k {                       /* one period, seamless */
  from { transform: translateX(0) }
  to   { transform: translateX(-320px) }  /* = the sine period width */
}
```

Notes on the numbers:

- `205px` fall distance = groundY - releaseY - ball radius. Recompute
  it for a different chart height; it is not universal.
- `320px` wave shift = ONE period of the sine path. The path must be
  drawn at least one period wider than the viewport on each side or the
  loop shows an edge (a gap appears at the seam).
- `orbit-k` is exactly 360deg — a full turn loops with no jump. Any
  other end angle jumps at the loop point.

## 2. How to apply them

Two parts, always both:

**(a) The base state is the FINISHED pose.** The figure is complete
with zero animation. Keyframes only animate FROM a hidden state.

```css
.draw { stroke-dasharray: 1; stroke-dashoffset: 0; }  /* visible at rest */
```

**(b) Motion only lives inside the no-preference media query:**

```css
@media (prefers-reduced-motion: no-preference) {
  .draw  { animation: draw-k 0.75s cubic-bezier(0.4, 0, 0.2, 1) both; }
  .fill  { animation: fade-k 0.4s ease-out both; }
  .pop   { transform-box: fill-box; transform-origin: 50% 50%;
           animation: pop-k 0.38s cubic-bezier(0.2, 0.9, 0.3, 1.35) both; }
  .bar   { animation: grow-k 0.55s cubic-bezier(0.2, 0.8, 0.3, 1) both; }
  .swing { animation: swing-k 2.1s ease-in-out infinite alternate; }
  .orbit { animation: orbit-k 7s linear infinite; }
  .fall  { animation: fall-k 2.6s cubic-bezier(0.5, 0, 0.9, 0.55) infinite; }
  .wave  { animation: wave-k 3.4s linear infinite; }
}
```

Why this order matters (the common bug): if the base state were the
HIDDEN start (e.g. `.draw { stroke-dashoffset: 1 }` outside the media
query), reduced-motion users see a blank figure forever — the
animation that would reveal it never runs. Base = finished; keyframes
animate FROM hidden. Then reduced motion shows the same finished pose
instantly.

The `both` fill mode is required: it holds the `from` state before the
delay elapses and the `to` state after the animation ends, so staggered
elements do not flash their finished pose early.

## 3. Stagger and per-element timing

Per-element delay is an inline style on the element:

```jsx
<label
  className="pop"
  style={{ animationDelay: `${i * 90}ms` }}
/>
```

Per-body loop variation uses inline `animationDuration` and
`animationDirection` — AND the JS engines read those exact values back
(GSAP/anime pick up per-orbit speed and reverse direction from them):

```jsx
<g
  className="orbit"
  style={{
    transformBox: 'view-box',
    transformOrigin: '320px 210px',
    animationDuration: `${orbit.period}s`,
    animationDirection: orbit.dir === 'reverse' ? 'reverse' : 'normal',
  }}
/>
```

## 4. Transform origins on SVG

CSS transforms on SVG elements resolve against `transform-box`. You
must set it explicitly or the browser default (`view-box` for SVG
elements in most engines, but `border-box` mental models leak in from
HTML) produces rotation around the wrong point.

**Rule of thumb:**

- Rotating/scaling a GROUP around a physical point (pendulum pivot,
  orbit center, bar baseline): `transform-box: view-box` + origin in
  user units (px values measured from the SVG's top-left, the same
  coordinate system as `x=`/`y=` attributes).
- Popping an individual element from its own center (label, dot):
  `transform-box: fill-box` + `transform-origin: 50% 50%`.

Examples:

```jsx
{/* bar: grows out of the baseline, up or down */}
<rect
  className="bar"
  x={bx} y={by} width={bw} height={bh}
  style={{ transformBox: 'view-box', transformOrigin: '320px 246px' }}
/>

{/* pendulum: swings from the pivot, not from the chart origin */}
<g
  className="swing"
  style={{ transformBox: 'view-box', transformOrigin: '320px 52px' }}
>

{/* label: pops from its own center */}
className="pop"   /* class carries fill-box + 50% 50% (see section 2) */
```

Why the JS engines need the same numbers: GSAP writes the SVG
`transform` ATTRIBUTE (not CSS), so it ignores `transform-box` entirely
and needs `svgOrigin: '320 52'` — read it back from the inline style
and strip `px`. anime.js v4 drives CSS transforms, so the inline
`transform-box`/`transform-origin` apply automatically and it needs no
origin bookkeeping. Full mechanics: `gsap-timelines.md`.

## 5. The engine kill-switch class

When GSAP or anime drives a figure, CSS keyframes must NOT also run
(rule 1 in SKILL.md). The dispatcher adds `viz-lib` to the wrapper and
this block turns every animation off beneath it:

```css
/* inside the figure's own CSS scope */
&.viz-lib .draw,
&.viz-lib .fill,
&.viz-lib .pop,
&.viz-lib .bar,
&.viz-lib .swing,
&.viz-lib .orbit,
&.viz-lib .fall,
&.viz-lib .wave {
  animation: none !important;
}
```

The class decision happens at PARSE time (same on server and client)
so there is no first-paint flash where CSS starts a tween GSAP is
about to fight over.

Related wrapper classes:

```jsx
<figure className={driven ? 'viz viz-lib' : 'viz'} data-engine={engine}>
```

- `viz` — the figure box (layout, background, caption).
- `viz-lib` — CSS animations killed beneath (JS engine active).
- `data-engine` — `gsap | anime | three | physics | css | manim`; QA
  pages count these to prove wiring.

## 6. Rough.js — sketchy geometry generation

Rough.js produces MARKUP (path data), not motion. Animate its output
with the keyframes above or with GSAP/anime.

```js
import rough from 'roughjs';

const gen = rough.generator();
const drawable = gen.rectangle(x, y, w, h, {
  stroke: 'currentColor',
  strokeWidth: 2,
  roughness: 1.1,     // 0 = ruled, 1-2 = hand-drawn, 3+ = scribble
  seed: 7,            // SAME seed = same wobble on every re-render
});
const paths = gen.toPaths(drawable);

// stroke paths -> className="draw" pathLength={1}  (they draw on)
// fill paths  -> className="fill" with a CSS-var color
```

Rules:

- **Fix the `seed` per shape.** Without it, every re-render generates
  new wobble and the figure twitches on unrelated state changes.
- **Rough computes fill colors itself**; override them via a CSS
  variable so figures inherit theme palettes:
  `style={{ fill: 'var(--figure-fill)' }}` on fill paths.
- Only path DATA comes from Rough. Classes, keys, transform origins,
  and accessibility stay in your own renderer — the generator never
  owns markup structure.
- Available primitives: `rectangle`, `ellipse`, `circle`, `line`,
  `linearPath`, `polygon`, `curve`, `path`. Points are in the same
  user units as the rest of the SVG.

## 7. When CSS alone is the right choice

- The figure must work with JS disabled or on first paint before the
  engine chunk arrives (CSS is in the critical stylesheet).
- Reduced motion is the common case (CSS needs no guard code beyond
  the media query).
- The animation is one of the eight built-in kinds — draw, fade, pop,
  grow, swing, orbit, fall, wave — with simple stagger.
- Bundle budget forbids even gsap (~70KB gzip).

Reach for GSAP/anime when: multi-stage timelines, sequencing chrome
before content, scrubbing/controlling progress, per-element custom
easing, or coordinating several figures on one timeline.
