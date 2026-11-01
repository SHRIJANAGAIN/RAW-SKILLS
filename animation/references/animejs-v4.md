# anime.js v4 — full reference

anime.js v4 is the alternate SVG/DOM engine: same jobs as GSAP
(draw-on, pops, bars, loops) with different easing names and a
keyframe-array style. This file is the complete API surface this skill
uses.

Contents:
1. Install and the v3-vs-v4 import trap
2. Named exports used here
3. The complete runner (with cleanup)
4. Draw-on, pops, bars
5. The four loops (swing, orbit, wave, fall-with-keyframes)
6. Eases and stagger
7. Why SVG needs no origin bookkeeping
8. Cleanup with `revert()`
9. Gotchas

---

## 1. Install and the import trap

```bash
npm i animejs        # v4.5.x ships its OWN TypeScript types
```

v4 changed the API shape. The v3 one-liner is GONE:

```js
// v3 (DEAD on a v4 install — "anime is not a function"):
import anime from 'animejs';
anime({ targets: '.x', opacity: [0, 1] });

// v4 (correct):
import { animate } from 'animejs';
animate('.x', { opacity: [0, 1] });
```

Verify which version is installed:

```bash
node -e "import('animejs').then(m => console.log(typeof m.animate))"
# -> function   = v4
# -> undefined  = v3 (default export) — upgrade or write v3 code
```

## 2. Named exports used here

```js
const { animate, set, stagger } = await import('animejs');
```

| export | purpose |
|---|---|
| `animate(targets, params)` | creates and starts an Animation; returns a handle with `.revert()` / `.pause()` / `.play()` |
| `set(targets, params)` | applies values instantly (no animation); used for pre-state like dasharray |
| `stagger(n)` | a function yielding `n`ms increments per target index (v4 form: `stagger(90)`) |

Dynamic import inside the effect (same rule as every engine — see
SKILL.md rule 6): `await import('animejs')` (~20KB gzip, code-split).

## 3. The complete runner

```jsx
useEffect(() => {
  const root = rootRef.current;
  if (root === null) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  let dead = false;
  let cleanup;
  runAnime(root).then(kill => {
    if (dead) kill();
    else cleanup = kill;
  });
  return () => {
    dead = true;
    cleanup?.();
  };
}, [rootRef]);

async function runAnime(root) {
  const { animate, set, stagger } = await import('animejs');
  const q = sel => Array.from(root.querySelectorAll(sel));

  const chrome = q('.title, .axis, .grid, .tick, .label, .guide');
  const draws  = q('.draw');
  const fills  = q('.fill');
  const pops   = q('.pop, .dot');
  const bars   = q('.bar');
  const swings = q('.swing');
  const orbits = q('.orbit');
  const falls  = q('.fall');
  const waves  = q('.wave');

  const anims = [];

  // (1) chrome first
  if (chrome.length) {
    anims.push(animate(chrome, {
      opacity: [0, 1], duration: 250, delay: stagger(15),
      ease: 'outQuad',
    }));
  }

  // (2) draw-on: set the pre-state, then animate the offset to 0
  if (draws.length) {
    set(draws, { strokeDasharray: '1', strokeDashoffset: 1 });
    anims.push(animate(draws, {
      strokeDashoffset: 0, duration: 800, delay: stagger(90),
      ease: 'inOutQuad',
    }));
  }

  // (3) fills, then pops with overshoot
  if (fills.length) {
    anims.push(animate(fills, {
      opacity: [0, 1], duration: 350, delay: stagger(40), ease: 'outQuad',
    }));
  }
  if (pops.length) {
    anims.push(animate(pops, {
      opacity: [0, 1], scale: [0.5, 1], duration: 430,
      delay: stagger(70), ease: 'outBack',
    }));
  }

  // (4) bars grow from baseline (transform-origin comes from inline CSS)
  if (bars.length) {
    anims.push(animate(bars, {
      scaleY: [0, 1], duration: 560, delay: stagger(90), ease: 'outQuad',
    }));
  }

  // loops (section 5) ... push each handle into anims ...

  return () => { for (const a of anims) a.revert(); };
}
```

Note: anime takes exactly ONE `delay` per params object. For "start
after a fixed offset, then stagger", write a single function:
`delay: (el, i) => 100 + i * 90` — never list `delay` twice in one
object literal; the later key silently wins.

## 4. Draw-on, pops, bars — parameter detail

**Draw-on.** The pre-state must be set separately (v4 has no `from`
tween — `set` then `animate`):

```js
set(paths, { strokeDasharray: '1', strokeDashoffset: 1 });
const a = animate(paths, {
  strokeDashoffset: 0,        // target value; start = value from `set`
  duration: 800,              // milliseconds
  delay: stagger(90),         // +90ms per path index
  ease: 'inOutQuad',
});
```

`pathLength="1"` on the markup is what makes `dasharray: '1'` mean
"the whole path" (see SKILL.md rule 2).

**Pops.** Value arrays `[from, to]`:

```js
animate(pops, {
  opacity: [0, 1],
  scale: [0.5, 1],
  duration: 430,
  delay: stagger(70),
  ease: 'outBack',            // overshoot past 1, then settle
});
```

**Bars.** `scaleY: [0, 1]` — vertical growth only. The transform
origin (baseline in view-box units) comes from the inline CSS the
markup already carries; anime v4 drives CSS transforms so it applies
automatically (section 7).

## 5. The four loops

### Swing (pendulum)

```js
const a4 = animate(swing, {
  rotate: [-24, 24],
  duration: 1050,
  ease: 'inOutSine',
  loop: true,        // repeat forever
  alternate: true,   // play forward then backward (the CSS `alternate`)
});
```

### Orbit (one full turn, per-body speed)

```js
const durMs = parseFloat(o.style.animationDuration || '7') * 1000;
const reverse = o.style.animationDirection === 'reverse';
const a5 = animate(orbit, {
  rotate: reverse ? [360, 0] : [0, 360],   // reverse = negative direction
  duration: durMs,
  ease: 'linear',
  loop: true,
});
```

Speed and direction come from the same inline CSS the CSS path used —
the engine swap does not change per-body behaviour.

### Wave (seamless translate)

```js
const a6 = animate(wave, {
  x: [0, -320],       // ONE sine period; path must be wider by that much
  duration: 3400,
  ease: 'linear',
  loop: true,
});
```

### Fall (multi-stage bounce with keyframes)

anime v4 keyframe arrays are per-step — each entry can carry its own
`duration` and `ease`:

```js
const a7 = animate(fall, {
  y: [
    { value: 205, duration: 750,  ease: 'inQuad' },   // fall
    { value: 159, duration: 300,  ease: 'outQuad' },  // bounce 1
    { value: 205, duration: 260,  ease: 'inQuad' },
    { value: 191, duration: 160,  ease: 'outQuad' },  // bounce 2
    { value: 205, duration: 120,  ease: 'inQuad' },
    { value: 205, duration: 1010 },                   // idle to loop point
  ],
  loop: true,
});
```

Parallel properties must cover the SAME total duration or they drift
out of phase and the ball reappears mid-air. The opacity fade (hide
the teleport back to the top) is a second animation whose step
durations sum to the identical total (750+300+260+160+120+1010 =
2600):

```js
const a8 = animate(fall, {
  opacity: [
    { value: 1, duration: 2340 },   // visible for the whole cycle...
    { value: 0, duration: 260 },    // ...fades out at the reset
  ],
  loop: true,
});
```

If the sums differ, the loop points disagree and the animation jumps.

## 6. Eases and stagger

v4 ease names (string form):

| name | feel |
|---|---|
| `linear` | constant speed (orbits, waves) |
| `outQuad` | fast start, gentle settle (bars, fills) |
| `inQuad` | accelerating (falls, drops) |
| `inOutQuad` | ease both ends (draw-on) |
| `outCubic` | snappy settle |
| `inOutSine` | smooth back-and-forth (pendulum) |
| `outBack` | overshoot past the target, then settle (pops) |
| `inElastic` | rubber-band start |
| `outBounce` | bounces at the end |

Function form for tuning: `ease: 'outBack(1.6)'` (the number is the
tension argument).

`stagger(n)` returns an index-based delay function: target 0 gets 0ms,
target 1 gets `n` ms, target 2 gets `2n`... It works on every property
that accepts a function, but `delay` is the usual place:

```js
delay: stagger(70)              // 0, 70, 140, ... ms
delay: stagger(70, { start: 300 }) // begin the cascade at 300ms (v4 form)
```

## 7. Why SVG needs no origin bookkeeping

anime v4 drives CSS transforms (`x`/`y` translate, `rotate`, `scale`),
not SVG attribute transforms. CSS transforms on SVG resolve against
the element's `transform-box` — which the markup already set inline:

```jsx
<g className="swing"
   style={{ transformBox: 'view-box', transformOrigin: '320px 52px' }}>
```

So `rotate: [-24, 24]` on that group pivots around (320, 52)
automatically. That is the whole difference from GSAP, which writes
the SVG `transform` ATTRIBUTE and needs explicit `svgOrigin` (see
`gsap-timelines.md` section 5). Nothing extra is required here — but
the inline origins must exist, or anime rotates around the same wrong
default as plain CSS would (see `svg-css-baseline.md` section 4).

## 8. Cleanup with `revert()`

Every `animate()` handle must be reverted:

```js
return () => { for (const a of [a1, a2, a3, a4, a5, a6, a7, a8]) a.revert(); };
```

`revert()` does two things at once:

1. cancels the animation (stops all loops — `loop: true` included), and
2. restores every value it touched to what it was before it started.

That second half is why reverting beats `pause()` — the figure returns
to its clean static markup, so a React remount re-runs the effect on
pristine DOM instead of a half-animated state. Collect ALL handles
(including ones from the loops section) into one array if that is
simpler; the invariant is: every handle gets exactly one `revert()`.

`set()` calls need no cleanup — they are not animations — but their
values are restored when a `revert()` runs on a later animation of the
same element only if the set happened inside that animation. When in
doubt, re-`set()` the pre-state at the start of the next run; it is
idempotent.

## 9. Gotchas

- **`animate is not a function`** = v3 import on v4 (section 1).
- **Duplicated `delay` key** in one params object — the last silently
  wins (section 3 note).
- **Phase drift** in multi-property keyframes — totals must match
  exactly (section 5).
- **`loop: true` never stops by itself** — only `revert()` does.
- **Reduced motion** — skip the whole runner (the effect returns
  before importing); the static base state is the finished figure.
- **`alternate` vs `loop`** — `alternate: true` without `loop` plays
  once forward-back; you need BOTH for an infinite yoyo.
- **Combined selectors** — one query per element
  (`'.pop, .dot'`), so no element enters two animations.
