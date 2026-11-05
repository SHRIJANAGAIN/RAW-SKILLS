# Three.js 3D solids — full reference

Three.js renders real 3D objects (cube, cylinder, cone, sphere, prism,
any 2D shape extruded into a slab) where an SVG would be a lie. One
WebGL canvas per figure, loaded on demand, destroyed on unmount, with
a flat 2D fallback when WebGL is unavailable.

Contents:
1. Install (types included)
2. Scene setup: renderer, camera, stage
3. Geometry map (every shape)
4. 2D -> 3D extrusion (the catch-all)
5. Materials, inked edges, lights
6. Rotate loop, resize, reduced motion
7. Full teardown
8. Failure ladder and the flat fallback
9. Stage CSS
10. Gotchas

---

## 1. Install

```bash
npm i three            # v0.186.x — ships NO types
npm i -D @types/three  # v0.186 — required, or TS errors
```

Import on demand inside the effect (~170KB gzip chunk — this must
never sit in the entry bundle):

```js
const THREE = await import('three');
```

Verify:

```bash
node -e "import('three').then(m => console.log(typeof m.Scene))"
# -> function
```

## 2. Scene setup

Fixed 16:9 stage, camera slightly above and in front so the object
reads with depth:

```js
const THREE = await import('three');

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(38, 16 / 9, 0.1, 60);
camera.position.set(0, 1.85, 4.7);   // y up, z toward viewer
camera.lookAt(0, 0, 0);              // aim at the origin

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
// antialias: smooth edges; alpha: transparent canvas over figure bg
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
stageDiv.append(renderer.domElement);
```

Parameter reasoning:

- **fov 38** — moderate telephoto; less perspective distortion than
  the default 50+ so cubes look square, not barrelled.
- **position (0, 1.85, 4.7)** — looking slightly down at the object;
  4.7 units back frames a ~1.3-unit object in a 16:9 view at fov 38.
- **`pixelRatio` must be a NUMBER** — `Math.min(2, devicePixelRatio)`.
  The string `'device'` is a different library's option; with the types
  installed this is a compile error, without them it is a runtime
  blurry/shrunk canvas.
- **`alpha: true`** — the canvas shows the figure's CSS background
  (theme-aware) instead of forcing a colour.

`render.setSize` details are in section 6 (resize).

## 3. Geometry map

One geometry per shape family. All sizes are in world units — keep
max dimension near 1.3-1.9 so the camera framing above stays valid:

| shape | geometry |
|---|---|
| cube | `new THREE.BoxGeometry(1.3, 1.3, 1.3)` |
| cuboid / box | `new THREE.BoxGeometry(1.9, 1.15, 1.15)` |
| cylinder | `new THREE.CylinderGeometry(0.8, 0.8, 1.7, 36)` (radiusTop, radiusBottom, height, radialSegments) |
| cone | `new THREE.ConeGeometry(0.95, 1.7, 36)` |
| sphere | `new THREE.SphereGeometry(1, 40, 26)` (radius, widthSegments, heightSegments) |
| pyramid | `new THREE.ConeGeometry(1.15, 1.6, 4).rotateY(Math.PI / 4)` — 4 segments = square base, rotated so a face looks at camera |
| prism (triangular) | extrude a 3-point polygon (section 4) |
| rectangle / quadrilateral / parallelogram | extrude the 4-point polygon |
| triangle (flat slab) | extrude the 3-point polygon |
| circle (flat disc) | extrude `Shape.absarc(0, 0, 0.95, 0, Math.PI * 2)` |

Higher `radialSegments`/`widthSegments` = smoother curve; 36/40/26
are plenty at inline-figure size and keep vertex counts small.

Sphere is the one shape that must NOT use flat shading (section 5).

## 4. 2D -> 3D extrusion (the catch-all)

Any flat polygon becomes a slab — so the same 2D vocabulary the rest
of the app uses (triangle points, rectangle corners, circle radius)
answers 3D directly:

```js
function extrude(THREE, pts) {
  const s = new THREE.Shape();
  pts.forEach(([x, y], i) => (i === 0 ? s.moveTo(x, y) : s.lineTo(x, y)));
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, {
    depth: 0.55,        // slab thickness (z)
    bevelEnabled: false, // crisp diagram edges, no rounded lip
  });
  g.translate(0, 0, -0.275);  // center the slab on z = 0 so rotation
  return g;                    // shows both faces symmetrically
}
```

Usage for a triangle with points in world units:

```js
const geo = extrude(THREE, [[-0.8, -0.55], [0.8, -0.55], [0, 0.75]]);
```

Why `-0.275`: ExtrudeGeometry builds z in `[0, depth]`; without the
translate the slab is off-centre and spins lopsided.

Scale note: keep 2D point magnitudes near the table's sizes (0.5-1.0).
A polygon spanning 400 SVG pixels would be far outside the camera
frame — divide screen-unit coordinates down to world units first (a
single `scale = 1.4 / maxExtent` factor is enough).

## 5. Materials, inked edges, lights

```js
const group = new THREE.Group();

group.add(
  new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({
      color: 0xeef2ff,      // near-white body so edges read dark
      roughness: 0.7,
      metalness: 0.04,
      flatShading: shape !== 'sphere',  // facets on polyhedra only
    }),
  ),
  new THREE.LineSegments(
    new THREE.EdgesGeometry(geo, 30),   // 30-degree edge threshold
    new THREE.LineBasicMaterial({ color: 0x0f172a }),  // ink lines
  ),
);

scene.add(group);

scene.add(new THREE.AmbientLight(0xffffff, 1.0));
const key = new THREE.DirectionalLight(0xffffff, 1.5);
key.position.set(3, 5, 4);
const rim = new THREE.DirectionalLight(0xffffff, 0.6);
rim.position.set(-4, 2, -3);
scene.add(key, rim);
```

Why each piece matters:

- **`EdgesGeometry(geo, 30)`** draws the outline where two faces meet
  at more than 30 degrees — this is what makes a solid read as a
  DIAGRAM (dark ink lines) rather than a soft blob. Cubes/cylinders/
  pyramids get full outlines; a sphere has no such edges, so it is
  shaded only.
- **`flatShading: true`** makes each face a uniform tone (faceted,
  diagram-like) — correct for polyhedra, WRONG for a sphere where it
  produces visible banding (the segments become flat rings). Hence
  `shape !== 'sphere'`.
- **Three lights**: ambient fills shadows to near-white (matches the
  light figure background), key gives directional form from upper
  right, rim separates the object from the background at the left
  edge. No shadows needed (no `castShadow` — expensive, invisible at
  this size).
- Body colour near-white + dark edge lines = the same ink-on-paper
  look the SVG figures use.

## 6. Rotate loop, resize, reduced motion

```js
const fit = () => {
  const w = Math.max(240, stageDiv.clientWidth);   // never 0 mid-layout
  const h = Math.round(w * 0.5625);                // 16:9
  renderer.setSize(w, h, false);                   // false = don't touch CSS
  camera.aspect = w / h;
  camera.updateProjectionMatrix();                 // aspect changed -> must update
  renderer.render(scene, camera);                  // redraw the new size now
};
fit();
window.addEventListener('resize', fit);
```

`setSize(w, h, false)`: the `false` stops three from writing inline
px width/height on the canvas — CSS (`width/height: 100%`) owns the
layout, the renderer owns the backing buffer.

Loop and reduced motion:

```js
let raf = 0;
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  renderer.render(scene, camera);   // one honest frame, no motion
} else {
  const tick = () => {
    group.rotation.y += 0.012;      // rad/frame @60fps -> ~10s per turn
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);
}
```

- Reduced motion still gets a REAL rendered frame (correct lighting,
  correct geometry) — not a blank canvas and not the SVG fallback.
- 0.012 rad/frame × 60 = 0.72 rad/s ≈ 8.7s per revolution. Slow and
  readable; figure captions need time.

## 7. Full teardown

```js
cancelAnimationFrame(raf);                  // 1. stop the loop FIRST
window.removeEventListener('resize', fit);  // 2. no calls into a dead renderer
geo.dispose();                              // 3. GPU buffers
renderer.dispose();                         // 4. WebGL context resources
renderer.domElement.remove();               // 5. detach the canvas
```

Ordering: if the loop or a resize fires after `dispose()`, three
throws (or silently warns) on a dead context. Stop callbacks first,
free GPU memory, then remove the element.

`EdgesGeometry`/materials are also GPU resources; `renderer.dispose()`
plus losing the context covers them in practice, but for completeness
you may dispose each explicitly right after `geo.dispose()`:

```js
mesh.material.dispose();
edgeLines.material.dispose();   // whatever handles hold them
```

In React StrictMode the double effect must reach this teardown or you
see two stacked canvases — a visible symptom of missing `remove()`.

## 8. Failure ladder and the flat fallback

Handle failures in this order:

1. **`new THREE.WebGLRenderer(...)` throws** (blocklisted GPU, old
   WebView, `--disable-gpu`): wrap construction in try/catch and show
   the flat 2D version of the same shape, or an honest card —
   "3D view is not available on this device". Never a raw exception
   boundary.

   ```js
   let renderer;
   try {
     renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
   } catch {
     return renderFlat2D(spec);   // SVG version already exists
   }
   ```

2. **Shape has no 3D meaning** (an angle, parallel lines — ideas about
   LINES, not solids): flat version by choice, no error state at all.

3. **Any runtime throw later** (geometry construction for unknown
   shape): same flat fallback — the figure never DEPENDS on WebGL
   arriving.

Invariant: the 2D rendering of every shape must be valid on its own;
3D is an enhancement layer. That is also why the dispatcher renders the
static body first and only swaps it when three actually mounts.

## 9. Stage CSS

```css
.viz-three-stage {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: 10px;
}
.viz-three-stage canvas {
  display: block;
  width: 100% !important;   /* beats three's inline px (setSize false) */
  height: 100% !important;
}
```

`aspect-ratio` reserves space before the canvas exists — no layout
jump when the chunk loads and appends. Keep the stage width inside the
figure column (the 16:9 height then follows automatically).

## 10. Gotchas

- **`@types/three` missing** -> "Could not find a declaration file
  for module 'three'". Install the matching major (0.186 types for
  0.186 three).
- **`pixelRatio: 'device'`** is invalid here — must be a number
  (section 2).
- **Sphere + `flatShading: true`** = banded ring artifact — exclude
  only the sphere (section 5).
- **Cube spins around a corner** = camera/geometry not centred —
  remember the extrude translate and keep shapes near origin.
- **Canvas stretched tall/skinny** = `camera.aspect` not updated in
  `fit()`; always pair `setSize` with `updateProjectionMatrix`.
- **Blank canvas but no error** = reduced-motion path with zero render
  calls — the single-frame render (section 6) is mandatory in that
  branch.
- **Two stacked canvases in dev** = StrictMode double effect without
  teardown (section 7).
- **Chunk never loads** = top-level `import 'three'` was avoided but
  the effect also must be reached — mount a figure, then check the
  network tab for the three chunk.
