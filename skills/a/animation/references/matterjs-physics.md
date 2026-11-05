# Matter.js physics worlds — full reference

Matter.js replaces ANIMATION with a real simulation: gravity,
collisions, constraints. The figure's own SVG chrome (axes, ground
line, orbit rings, labels) sits behind a transparent physics canvas on
top — so physics and diagram share one figure.

Contents:
1. Install (types included)
2. Loading (the CJS interop that is not optional)
3. Boot: engine, runner, render, canvas CSS
4. Invisible static bodies
5. Recipe A: pendulum
6. Recipe B: free fall + bounce
7. Recipe C: orbits (steered Kepler)
8. Recipe D: spring wave
9. Teardown (strict order)
10. Reduced motion and fallbacks
11. Gotchas

---

## 1. Install

```bash
npm i matter-js            # v0.20.x — UMD/CJS build, NO types
npm i -D @types/matter-js  # v0.20 — required, or TS errors
```

Import on demand (~90KB gzip chunk):

```js
const mod = await import('matter-js');
```

## 2. The CJS interop (not optional)

Webpack/Next wrap the UMD build so the actual API lands on `.default`:

```js
const M = mod.default ?? mod;
// M.Engine.create(...)   <- correct
// mod.default.create     <- what you get without unwrapping
```

Symptom of skipping it: `M.Engine is undefined` or an import object
with no functions. Verify:

```bash
node -e "import('matter-js').then(m => console.log(typeof (m.default ?? m).Engine.create))"
# -> function
```

## 3. Boot

```js
const M = mod.default ?? mod;

const engine = M.Engine.create({
  gravity: { x: 0, y: 1, scale: 0.001 },   // world default
});
// y: 1 = downward (SVG y grows down); scale 0.001 = Matter's default
// strength — y: 0 for orbit/spring worlds where gravity would lie.

const render = M.Render.create({
  element: mountDiv,          // a wrapper div INSIDE the figure
  engine,
  options: {
    width: 640,               // world units == px at pixelRatio 1
    height: 360,              // match the SVG chrome viewBox
    background: 'transparent',// SVG chrome shows through
    wireframes: false,        // use render.fillStyle, not debug lines
    pixelRatio: Math.min(2, window.devicePixelRatio),  // NUMBER, not 'device'
  },
});

const runner = M.Runner.create();
M.Runner.run(runner, engine);   // physics stepping
M.Render.run(render);           // canvas drawing (its own rAF)
```

- Two loops are now running: runner steps physics at fixed dt, render
  draws every frame. Both are stopped in section 9.
- `pixelRatio` must be a number here too (same trap as three).
- World coordinates are chosen to match the figure's SVG viewBox
  (640xH) so chrome lines and bodies line up exactly.

Canvas CSS (matter writes inline px; the `!important` wins):

```css
.viz-physics-wrap {
  position: relative;
  aspect-ratio: 640 / 360;        /* wrapper reserves the box */
}
.viz-physics-wrap canvas {
  position: absolute;
  inset: 0;
  width: 100% !important;
  height: 100% !important;
}
```

And in the figure, SVG chrome comes FIRST in the DOM, wrapper SECOND —
the canvas overlays the diagram:

```jsx
<figure className="viz viz-physics" data-engine="physics">
  <svg viewBox="0 0 640 360" className="viz-physics-chrome">
    {/* axes, ground line, orbit rings, labels — drawn behind */}
  </svg>
  <div ref={mountRef} className="viz-physics-wrap" />
</figure>
```

## 4. Invisible static bodies

Matter draws EVERY body. Statics (ground, walls, sun) must exist for
physics but not be seen — hide them with fully transparent paint
(there is no reliable `render.visible` for this across builds):

```js
const invisible = {
  isStatic: true,
  render: { fillStyle: 'rgba(0,0,0,0)', strokeStyle: 'rgba(0,0,0,0)' },
};

const ground = M.Bodies.rectangle(320, 301, 700, 10, invisible);  // y = centre
const wallL  = M.Bodies.rectangle(-12, 150, 24, 500, invisible);
const wallR  = M.Bodies.rectangle(652, 150, 24, 500, invisible);
M.Composite.add(engine.world, [ground, wallL, wallR]);
```

`rectangle(x, y, w, h)` takes the CENTRE point — a body at y=301 with
height 10 has its top face at y=296. Every drop-distance arithmetic in
the recipes below uses those top-face numbers.

Walls keep bouncing bodies inside the world so nothing falls out
during a long loop.

## 5. Recipe A: pendulum

```js
const DEG = Math.PI / 180;
const px = 320, py = 52, len = 190;      // pivot (matches SVG origin 320px 52px)
const startDeg = -24;

const bob = M.Bodies.circle(
  px + Math.sin(startDeg * DEG) * len,    // start displaced LEFT
  py + Math.cos(-startDeg * DEG) * len,   // y from the pivot down the rod
  21,                                     // radius
  {
    restitution: 0,            // no bounce on the bob itself
    frictionAir: 0.006,        // slow energy loss -> swings a good while
    density: 0.002,            // heavier than default -> air drag matters less
    render: { fillStyle: '#0437f2' },
  },
);

const arm = M.Constraint.create({
  pointA: { x: px, y: py },    // fixed world pivot
  bodyB: bob,                   // attached to the bob centre
  length: len,
  stiffness: 0.95,              // ~rigid rod; lower = rubbery
  render: { strokeStyle: '#64748b', lineWidth: 1.5 },  // the visible string
});

M.Composite.add(engine.world, [bob, arm]);
```

Physics notes:

- Gravity does ALL the work — there is no manual rotation. The
  constraint holds the distance; the bob swings because the start
  position is not the equilibrium.
- `stiffness: 0.95` reads as a rigid rod. Below ~0.9 the string
  visibly stretches at the swing bottom.
- `frictionAir` decides how many swings before it settles at bottom.
  0.006 ≈ 15-20 visible swings; 0.02 ≈ 4-5.
- The string is matter's constraint render (its own stroke line), so
  it stretches/slumps correctly during teardown-free operation.

## 6. Recipe B: free fall + bounce

```js
// world: default gravity (y: 1)
const ground = M.Bodies.rectangle(320, 301, 700, 10, invisible);  // top face 296

const ball = M.Bodies.circle(
  300, 74, 17,                            // release point, radius 17
  {
    restitution: 0.45,        // 0-1: fraction of speed kept per bounce
    frictionAir: 0.001,       // near vacuum; drop stays crisp
    density: 0.004,           // heavier -> gravity dominates drag
    render: { fillStyle: '#0437f2' },
  },
);
M.Composite.add(engine.world, [ground, ball]);
```

Distance math (the number CSS/GSAP used for the same figure):

    drop = groundTop - releaseY - radius
    drop = 296 - 74 - 17 = 205   -> ball rests exactly on the line

`restitution` decay gives the shrinking bounces: 0.45 first bounce
returns ~45% of impact speed (that is why bounce 1 rises 46px, bounce 2
~14px — same numbers as the `fall-k` keyframe).

Looping: physics has no built-in loop. Options, in order of
preference —
1. Keep it a single honest simulation (it settles and rests: a valid
   finished state).
2. On `afterUpdate`, if the ball has rested for N ms, teleport it back
   to the release point (`M.Body.setPosition`, `setVelocity({x:0,y:0})`)
   and let it fall again.

## 7. Recipe C: orbits (steered Kepler)

Matter has NO central gravity. The honest trick: keep a real physics
world (gravity 0) and steer every planet toward circular speed each
tick — Kepler-consistent (inner planets faster), stable for hours.

```js
// world: gravity { y: 0 } — space!
const cx = 320, cy = 180;

const sun = M.Bodies.circle(cx, cy, 16, {
  isStatic: true,
  render: { fillStyle: '#f59e0b' },     // the only VISIBLE static
});
// SVG orbit rings (dashed circles) are chrome drawn behind the canvas.

function planet(r, dir) {
  const b = M.Bodies.circle(cx + r, cy, 7, {
    frictionAir: 0,          // no drag — the stepper manages speed
    restitution: 1,
    render: { fillStyle: '#0437f2' },
  });
  return { body: b, dir };   // dir: +1 counter-clockwise, -1 clockwise
}

const planets = [planet(60, 1), planet(110, -1)];
M.Composite.add(engine.world, [sun, ...planets.map(p => p.body)]);

const step = () => {
  for (const p of planets) {
    const dx = p.body.position.x - cx;
    const dy = p.body.position.y - cy;
    const r = Math.hypot(dx, dy) || 1;
    const v = 1.35 * Math.sqrt(96 / r);          // v = sqrt(k/r), k = 96
    const wx = (-dy / r) * v * p.dir;            // tangential unit ...
    const wy = (dx / r) * v * p.dir;             // ... times speed, times spin
    M.Body.setVelocity(p.body, {
      x: p.body.velocity.x + (wx - p.body.velocity.x) * 0.08,   // lerp 8%
      y: p.body.velocity.y + (wy - p.body.velocity.y) * 0.08,
    });
  }
};
M.Events.on(engine, 'beforeUpdate', step);
```

Why this works:

- **`v = sqrt(k/r)`** is circular-orbit speed for a 1/r^2 attraction
  (Kepler): inner bodies move faster — the two planets visibly differ.
  `k = 96` is tuned for world units; `1.35` lifts it so orbits do not
  decay under the lerp.
- **The 0.08 lerp** nudges velocity toward the ideal tangential value
  each tick instead of overwriting it — radial drift is damped, motion
  stays smooth, no jitter.
- **`dir`** flips the tangential direction for retrograde motion.
- The sun is a static painted amber; planet-planet gravity is not
  modelled (they steer past each other) — correct for a diagram.

`Events.on(engine, 'beforeUpdate', step)` must be recorded for
`Events.off` in section 9 — a leaked handler keeps mutating a cleared
world.

## 8. Recipe D: spring wave

Bodies pinned to moving anchors by soft constraints — the solver adds
organic lag no kinematic loop can fake.

```js
// world: gravity { y: 0 }
const x0 = 20, x1 = 620, mid = 180;
const period = 320, amp = 42, count = 13;

const balls = [];
const springs = [];
const anchors = [];

for (let i = 0; i < count; i++) {
  const x = x0 + (i * (x1 - x0)) / (count - 1);
  const anchor = { x, y: mid };                 // pointA object we MUTATE
  const ball = M.Bodies.circle(x, mid, 9, {
    density: 0.002,               // light -> follows the anchor eagerly
    frictionAir: 0.06,            // damps oscillation into a clean wave
    collisionFilter: { group: -1 },   // never collide with siblings
    render: { fillStyle: '#0437f2' },
  });
  const spring = M.Constraint.create({
    pointA: anchor,
    bodyB: ball,
    length: 0,                    // rest length zero: ball sits ON anchor
    stiffness: 0.045,             // soft -> the lag that makes it organic
    damping: 0.1,                 // kills per-ball ringing
    render: { visible: false },   // only the balls are drawn
  });
  anchors.push(anchor);
  balls.push(ball);
  springs.push(spring);
}
M.Composite.add(engine.world, [...balls, ...springs]);

// travelling sine: every tick move each anchor along the wave
let t = 0;
const wave = () => {
  t += 1;
  for (const a of anchors) {
    a.y = mid - Math.sin(((2 * Math.PI * (a.x - x0)) / period) - t * 0.031) * amp;
  }
};
M.Events.on(engine, 'beforeUpdate', wave);
```

Parameter reasoning:

- **`stiffness 0.045`** — soft enough that balls trail their anchors
  (the visible wave shape) but firm enough to return within one cycle.
  Raise for a rigid wave, lower for syrup.
- **`frictionAir 0.06`** — high: each ball settles onto its anchor
  value instead of ringing forever.
- **`group: -1`** — a shared negative collision group means
  "same group never collides"; without it neighbouring balls knock
  each other and the wave scatters.
- **`anchor` objects are mutated in place** — Matter reads `pointA`
  every step, so moving `a.y` moves the constraint's fixed end. This
  is intentional and the standard way to drive kinematic ends.
- **`t * 0.031`** phase speed + **period 320** match the SVG sine
  drawn in chrome, so the balls ride the printed curve. Keep them in
  sync with the path (320 also matches the CSS/GSAP wave shift).

## 9. Teardown (strict order)

```js
const offs = [];
M.Events.on(engine, 'beforeUpdate', handler);
offs.push(() => M.Events.off(engine, 'beforeUpdate', handler));
// ...one off() per Events.on, collected as you register...

return () => {
  for (const off of offs) off();   // 1. handlers FIRST — no more mutation
  M.Render.stop(render);           // 2. stops render's rAF
  M.Runner.stop(runner);           // 3. stops physics stepping
  M.Composite.clear(engine.world, false);  // 4. bodies + constraints
  M.Engine.clear(engine);          // 5. engine internals
  render.canvas.remove();          // 6. detach the canvas element
};
```

Why this order:

1. A `beforeUpdate` handler touching a cleared world throws — remove
   handlers before anything else dies.
2. `Render.stop` before `Runner.stop` is not strictly required, but
   stopping draw first means no frame renders against a soon-cleared
   world.
3. `Composite.clear(world, false)` — the `false` keeps the world's
   root container itself; `Engine.clear` then releases engine-level
   state.
4. `render.canvas.remove()` — leaving it makes React StrictMode's
   second effect append a SECOND canvas (visible doubling in dev).

Full cleanup in one line to remember: **off -> stop -> clear -> remove.**

## 10. Reduced motion and fallbacks

If `matchMedia('(prefers-reduced-motion: reduce)').matches`, skip the
ENTIRE boot (return before `Engine.create`). The SVG chrome alone —
axes, ground line, resting ball drawn at its rest position — is a
complete still figure. So the static markup must place bodies at rest
positions: the ball ON the ground line, the bob at the bottom of its
string, planets on their rings. Reduced motion then shows the
simulation's finished state without running it.

Same for WebGL-less situations — Matter uses 2D canvas, not WebGL, so
it is far more available; the guard is only about motion preference
and JS failure. If `Render.create` throws, show the chrome-only figure.

## 11. Gotchas

- **`M.Engine` undefined** = skipped the `mod.default ?? mod` unwrap
  (section 2).
- **Static bodies visible as grey boxes** = forgot transparent fills
  (section 4).
- **Body positions off by half its size** = `rectangle` takes CENTRE
  coordinates; compute top faces yourself (section 4).
- **`pixelRatio: 'device'`** invalid — number required (section 3).
- **Canvas stretched** = missing `width/height: 100% !important` CSS.
- **Doubled canvases in dev** = StrictMode without full teardown
  (section 9).
- **Wave scatters** = sibling collisions — `collisionFilter: { group: -1 }`.
- **Orbits decay into the sun** = lerp too weak or `k` too small —
  keep `0.08` lerp and the `1.35 * sqrt(96 / r)` formula.
- **Handler errors after unmount** = `Events.off` ran too late — it is
  step 1 for a reason.
- **Bodies drift after stop** = `Runner.stop` missing; the runner
  keeps stepping physics with no way to observe it.
