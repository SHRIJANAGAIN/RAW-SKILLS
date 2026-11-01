# Manim video pipeline — full reference

Manim (Community Edition) turns a generated Python scene into an mp4.
This file is the complete pipeline: install + smoke test, the shared
preamble, all three scene templates, the expression translation table,
the Node side (spawn, flags, timeout), output discovery, the hash
cache, in-flight dedupe, error summarizing, and the client player.

Contents:
1. Install and smoke test
2. The five pipeline rules
3. Shared preamble (colors, ticks, y-window)
4. Axes block
5. Scene template: plot
6. Scene template: area
7. Scene template: transform
8. Expression translation table
9. Node side: spawn, flags, timeout
10. Output discovery
11. Cache + in-flight dedupe
12. Error summarizing
13. Client player + fallback
14. Gotchas

---

## 1. Install and smoke test

```bash
pip install manim           # v0.22.x — bundles imageio-ffmpeg
python -m manim --version   # expect: Manim Community v0.22...
```

No system ffmpeg needed (imageio-ffmpeg ships one). No LaTeX needed —
this skill never uses `Tex`/`MathTex`.

Smoke test with the example next to SKILL.md:

```bash
python -m manim render -ql ../examples/plot_scene.py MyScene
```

Expected: `media/videos/plot_scene/480p15/MyScene.mp4` (a few MB).
The FIRST render takes ~10s longer (cold Python + Manim import).

Two environment notes for the Node side:

- Interpreter override: `process.env.PYTHON ?? 'python'` — some
  machines only have `py` or a venv activation.
- Manim writes `media/` relative to the CURRENT WORKING DIRECTORY of
  the spawned process — set `cwd` to a temp dir you control, never
  your app root.

## 2. The five pipeline rules

1. **Templates, never caller-supplied Python.** A typed spec fills one
   of the three fixed Scene templates below. Untrusted input must
   NEVER become code execution — an expression string is validated and
   translated (section 8), never pasted raw.
2. **Validate before rendering.** Compile the expression with the same
   evaluator the on-screen figure uses. If it fails, fall back to the
   static figure instead of burning 30s on a doomed render.
3. **Text, never Tex.** Every label is Pango `Text(...)`. A `Tex`
   object on a machine without a TeX distribution dies ~30s into the
   render with a LaTeX error buried in 8KB of output.
4. **Cache by content hash + dedupe in-flight.** Identical script ->
   identical video -> hash lookup. Concurrent identical requests
   share ONE render (section 11).
5. **Find the output recursively.** Folder naming
   (`videos/<stem>/<quality>/<Scene>.mp4`) varies with scene name
   stems and versions — walk the tree (section 10).

## 3. Shared preamble

Every generated scene file starts with exactly this (colors match the
app's figure palette; helpers give nice ticks and safe y-windows):

```python
from manim import *
import numpy as np

config.background_color = "#ffffff"

INK = "#0f172a"
BLUE = "#0437f2"
RED = "#e11d48"
MUTED = "#94a3b8"


def _step(span, target=5.0):
    """Nice axis tick spacing: 1/2/5 x 10^n around `target` divisions."""
    raw = max(abs(span), 1e-9) / target
    mag = 10.0 ** np.floor(np.log10(raw))
    norm = raw / mag
    unit = 1.0 if norm < 1.5 else 2.0 if norm < 3 else 5.0 if norm < 7 else 10.0
    return unit * mag


def _sample(fns, x0, x1, lo=None, hi=None):
    """Y-window from the curve(s); `lo`/`hi` override specific sides."""
    smin = smax = None
    if lo is None or hi is None:
        with np.errstate(all="ignore"):
            vals = np.array(
                [fn(float(t)) for t in np.linspace(x0, x1, 400) for fn in fns],
                dtype=float,
            )
        vals = vals[np.isfinite(vals)]
        if vals.size:
            smin, smax = float(vals.min()), float(vals.max())
    span = (
        1.0
        if smin is None or smax is None or smax - smin < 1e-9
        else smax - smin
    )
    if lo is None:
        lo = -1.0 if smin is None else smin - 0.18 * span
    if hi is None:
        hi = 1.0 if smax is None else smax + 0.18 * span
    if hi - lo < 1e-6:
        lo, hi = lo - 1.0, hi + 1.0
    return lo, hi
```

Why these helpers:

- `_step` — `Axes` wants an explicit tick step; raw division of the
  span gives 3.7-unit ticks. 1/2/5 x 10^n gives readable numbers.
- `_sample` — plots 400 points, DROPS non-finite values (tan asymptotes,
  log of negatives, sqrt of negatives) and pads 18% headroom. Without
  it, one `tan(x)` sample of 1e15 flattens the whole curve. The
  `lo`/`hi` overrides let a spec pin a window (`yMin`/`yMax`).
- `np.errstate(all="ignore")` — divide-by-zero warnings from sampling
  must not pollute (or fail) the render.

## 4. Axes block

Used by ALL three templates, after `ylo, yhi = _sample(...)`:

```python
axes = Axes(
    x_range=[x0, x1, _step(x1 - x0)],
    y_range=[ylo, yhi, _step(yhi - ylo)],
    x_length=10.0,
    y_length=5.4,
    tips=True,
    axis_config={"color": MUTED, "stroke_width": 2},
)
axes.add_coordinates(label_constructor=Text)   # Pango, never Tex
```

- `label_constructor=Text` is the project-wide "no LaTeX" decision —
  coordinate numbers render through Pango.
- `tips=True` gives arrowheads on both axes.
- `x_length`/`y_length` in MANIM UNITS (the frame is 14.22 wide) —
  10.0 x 5.4 sits centred with room for a title above.

## 5. Scene template: plot

The curve draws itself, marked points appear one by one.

```python
class MyScene(Scene):
    def construct(self):
        f = lambda x: <TRANSLATED PYTHON EXPR>
        x0, x1 = <xMin>, <xMax>
        ylo, yhi = _sample([f], x0, x1)          # or (…, lo=, hi=) if pinned

        axes = Axes(...)                          # section 4 block verbatim
        title = Text(<title>, font_size=26, color=INK).to_edge(UP, buff=0.2)

        self.play(Create(axes), run_time=0.7)
        self.play(Write(title), run_time=0.5)

        curve = axes.plot(f, color=BLUE, use_smoothing=True)
        self.play(Create(curve), run_time=2.2)    # the drawing-on moment

        for px, plabel in [<points>]:             # e.g. [(1.0, "2.0"), …]
            py = float(f(px))
            if not np.isfinite(py):
                continue
            py = min(max(py, ylo), yhi)           # clamp into the window
            dot = Dot(axes.c2p(px, py), color=RED, radius=0.07)
            lab = Text(str(plabel), font_size=20, color=RED).next_to(
                dot, UP, buff=0.16
            )
            self.play(FadeIn(dot, scale=0.4), Write(lab), run_time=0.45)

        self.wait(0.8)
```

Structure notes:

- `Create(curve)` is the stroke-draw animation — Manim's equivalent
  of the dashoffset draw-on. `use_smoothing=True` prevents kinked
  polylines on steep curves.
- Points are clamped into `[ylo, yhi]` so a dot never lands outside
  the axes (e.g. evaluated slightly beyond the sampled window).
- `self.wait(0.8)` — tail hold so the last label is readable before
  the video ends.

## 6. Scene template: area

Rectangles fill the space under the curve (Riemann sums). Same start
as plot through `self.play(Write(title)...)`, then:

```python
        curve = axes.plot(f, color=BLUE, use_smoothing=True)
        self.play(Create(curve), run_time=1.6)

        n = 14                              # rectangle count
        dx = (x1 - x0) / n
        rects = []
        for i in range(n):
            a = x0 + i * dx
            ya = float(f(a + dx / 2))      # midpoint height
            if not np.isfinite(ya):
                continue
            rects.append(
                Polygon(
                    axes.c2p(a, 0),
                    axes.c2p(a + dx, 0),
                    axes.c2p(a + dx, ya),
                    axes.c2p(a, ya),
                    fill_color=BLUE,
                    fill_opacity=0.35,
                    stroke_color="#93c5fd",
                    stroke_width=1.0,
                )
            )
        if rects:
            self.play(
                LaggedStart(
                    *[GrowFromEdge(r, DOWN) for r in rects],
                    lag_ratio=0.07,
                ),
                run_time=1.8,
            )
        self.wait(0.9)
```

- Midpoint sampling keeps each bar's height representative; points
  where `f` is non-finite are skipped (a `ln` curve simply stops
  filling where it does not exist).
- `GrowFromEdge(r, DOWN)` grows bars OUT OF the baseline — the video
  equivalent of `grow-k`/`scaleY` from the zero line.
- `LaggedStart(lag_ratio=0.07)` staggers the growth left-to-right.

## 7. Scene template: transform

One curve becomes another (`Transform` morphs the points):

```python
class MyScene(Scene):
    def construct(self):
        f = lambda x: <TRANSLATED OLD EXPR>       # before, BLUE
        g = lambda x: <TRANSLATED NEW EXPR>       # after, RED
        x0, x1 = <xMin>, <xMax>
        ylo, yhi = _sample([f, g], x0, x1)        # window covers BOTH

        axes = Axes(...)                          # section 4 block verbatim
        title = Text(<title>, font_size=26, color=INK).to_edge(UP, buff=0.2)

        self.play(Create(axes), run_time=0.7)
        self.play(Write(title), run_time=0.5)

        curve_f = axes.plot(f, color=BLUE, use_smoothing=True)
        self.play(Create(curve_f), run_time=1.5)

        lab_f = Text("y = <old display>", font_size=22, color=BLUE).to_edge(
            DOWN, buff=0.28
        )
        lab_g = Text("y = <new display>", font_size=22, color=RED).to_edge(
            DOWN, buff=0.28
        )
        self.play(Write(lab_f), run_time=0.4)

        curve_g = axes.plot(g, color=RED, use_smoothing=True)
        self.play(Transform(curve_f, curve_g), run_time=2.0)

        self.play(ReplacementTransform(lab_f, lab_g), run_time=0.5)
        self.wait(0.8)
```

- `_sample([f, g], ...)` — the window must contain BOTH curves or the
  morph flies off-frame.
- `Transform(curve_f, curve_g)` morphs in place; the label swaps via
  `ReplacementTransform` so text never overlaps mid-fade.

## 8. Expression translation table

The app evaluates expressions with its own parser (RPN evaluator);
the video side must produce THE SAME FUNCTION in numpy. One parser,
two backends — no drift. Translate token by token:

| app expr | python (numpy) |
|---|---|
| `sin(x)` | `np.sin(x)` |
| `cos(x)` | `np.cos(x)` |
| `tan(x)` | `np.tan(x)` |
| `sqrt(x)` | `np.sqrt(x)` |
| `ln(x)` | `np.log(x)` |
| `log(x)` | `np.log10(x)` |
| `abs(x)` | `np.abs(x)` |
| `a^b` | `a ** b` |
| `a % b` | `np.fmod(a, b)` |
| `pi` | `np.pi` |
| `tau` | `(2 * np.pi)` |
| `2x` (implicit multiply) | `(2 * x)` |

Implementation advice: replay the evaluator's RPN output directly to
emit Python — a token-by-token translation with parentheses around
every binary op. The safest sequence:

1. Compile the expression with the ON-SCREEN evaluator. Fail ->
   reject, static fallback (rule 2).
2. Emit python via the table (or RPN replay). ANY untranslatable token
   -> reject too; never pass the raw string through.
3. Only then build the scene file.

Never interpolate the raw user/model expression into the Python source
— that is arbitrary code execution on the render host.

## 9. Node side: spawn, flags, timeout

```js
import { spawn } from 'node:child_process';

const child = spawn(
  process.env.PYTHON ?? 'python',
  ['-m', 'manim', 'render', '-ql', '--format=mp4', 'scene.py', 'MyScene'],
  { cwd: tempDir, windowsHide: true },
);
```

Quality flags (pick ONE):

| flag | output | when |
|---|---|---|
| `-ql` | 480p15 | DEFAULT — inline figures; a few MB, fast |
| `-qm` | 720p30 | only when the user explicitly asks for quality |
| `-qh` | 1080p60 | only for a requested full-quality export |

Plus `--format=mp4` (explicit container; manim can default to others
depending on config) and the scene file + class name as the last two
arguments.

Timeout and output handling:

```js
const TIMEOUT = 150_000;              // cold import ~10s + scene render
let out = '';
const killTimer = setTimeout(() => {
  child.kill();
  reject(new Error('manim timeout'));
}, TIMEOUT);
child.stdout.on('data', d => { out += String(d); });
child.stderr.on('data', d => { out += String(d); });
// keep only the TAIL for error reporting:
if (out.length > 8192) out = out.slice(-8192);
```

- 150s covers cold renders comfortably; warm renders (import cached in
  the OS) take 5-15s at `-ql`.
- ANSI colour codes fill manim's progress output — strip them when
  reporting errors (section 12).
- ALWAYS `clearTimeout` + delete the temp dir in `finally`.

## 10. Output discovery

Never predict the path. Manim's folder naming depends on version and
the scene-name stem:

```js
import { readdir } from 'node:fs/promises';

const entries = await readdir(tempDir, {
  recursive: true,
  withFileTypes: true,
});
const hit = entries.find(e => e.isFile() && e.name.endsWith('.mp4'));
if (!hit) throw new Error('no mp4 produced');
const mp4Path = join(hit.parentPath ?? hit.path, hit.name);
```

Walk after the process exits 0 — but ALSO accept success-by-existence:
if the exit code is nonzero but an mp4 exists from a partial earlier
run, prefer the cached-file check (section 11) over re-deriving
anything. Real-world noise this avoids:

- `media/videos/<stem>/480p15/<Scene>.mp4` — normal layout
- `media/videos/<stem>/480p15/partial_movie_files/<Scene>/*.mp4` —
  per-animation SEGMENTS (find them, but they are NOT the final file;
  prefer a file named exactly `<Scene>.mp4`, else the top-level one)
- version-specific subfolder renames

Practical rule: search for `e.name === `${sceneName}.mp4`` FIRST,
fall back to any `*.mp4` deepest-first, and skip `partial_movie_files`
directories unless nothing else matches.

## 11. Cache + in-flight dedupe

```js
import { createHash } from 'node:crypto';

const hash = createHash('sha256').update(script).digest('hex').slice(0, 24);
const publicUrl = `/${dir}/${hash}.mp4`;
const publicPath = join(publicRoot, dir, `${hash}.mp4`);

// 1. already rendered?
try {
  await stat(publicPath);
  return publicUrl;
} catch { /* miss -> continue */ }

// 2. same request already rendering?
if (inFlight.has(hash)) return inFlight.get(hash);

// 3. render it — as ONE shared promise
const p = (async () => {
  const tempDir = await mkdtemp(...);
  try {
    await writeFile(join(tempDir, 'scene.py'), script);
    await runManim(tempDir);                 // section 9
    const mp4 = await findMp4(tempDir);      // section 10
    await mkdir(dirname(publicPath), { recursive: true });
    await copyFile(mp4, publicPath);
    return publicUrl;
  } finally {
    await rm(tempDir, { recursive: true, force: true });
    inFlight.delete(hash);                   // release waiters
  }
})();
inFlight.set(hash, p);
return p;
```

Three layers, why each exists:

1. **sha256[:24] of the SCRIPT** — same spec + same template = same
   bytes = same video. Re-opening a figure costs a `stat`.
2. **inFlight map** — ten simultaneous identical requests trigger ONE
   render, nine await it. Without it, identical concurrent renders
   stampede and fight over the same temp paths.
3. **temp dir in `finally`** — failed renders leave nothing behind.

The hash deliberately covers the whole script (template + preamble +
params), so any template/palette change invalidates old caches
automatically.

## 12. Error summarizing

Manim failures are verbose with ANSI box-drawing; keep the LAST useful
line:

```js
const clean = raw.replace(/\x1b\[[0-9;]*[A-Za-z]/g, '');
const line = clean
  .split(/\r?\n/)
  .map(l => l.replace(/\s+/g, ' ').trim())
  .filter(Boolean)
  .reverse()                                  // last meaningful line wins
  .find(l => /error|not found|no module/i.test(l)) ?? '';
const message = `manim exited ${code}: ${line}`.slice(0, 220);
```

- Reverse-then-find picks the final `Error ...` over earlier warnings.
- Cap ~220 chars — the UI shows one line; full output stays out of the
  model context entirely (and may contain paths/ANSI junk).
- ALWAYS delete the temp dir in `finally`, success or failure.

Common causes behind those last lines:

| last line mentions | cause |
|---|---|
| `TeX`, `LatexError`, `File "…sty"` | a `Tex`/`MathTex` entered the template — rule 3 violated |
| `No module named` | wrong interpreter (`PYTHON` env override needed) |
| `SyntaxError` | raw expression was pasted instead of translated — rule 1 violated |
| `FFMPEG`, `encoder` | ffmpeg missing — reinstall manim (imageio-ffmpeg bundles it) |

## 13. Client player + fallback

While the render promise is pending (first render can take ~30s
including cold import), show a wait card in the figure slot. When the
URL arrives:

```jsx
<video
  src={url}
  autoPlay
  loop
  muted
  controls
  playsInline
  onCanPlay={e => e.currentTarget.play().catch(() => {})}
/>
```

Why each attribute:

- `muted` + `autoPlay` + `playsInline` — the only combination every
  browser (including strict embedded webviews) allows without a user
  gesture. WITHOUT `muted`, autoplay is simply blocked.
- `controls` — the escape hatch: where autoplay is blocked anyway,
  playback via the controls always works.
- `loop` — figure videos are short and cyclical by design.
- `onCanPlay ... play().catch()` — retries playback after load; the
  `.catch()` swallows the (expected, harmless) autoplay rejection.
- `preload="metadata"` if bandwidth matters — frame 1 still shows.

On render failure: swap in the static figure of the same spec —
nothing in the UI ever DEPENDS on the video arriving (rule from the
five: the static figure is the universal fallback). Never show raw
error text to the reader; log the 220-char summary.

## 14. Gotchas

- **TeX crash ~30s in** = `Tex`/`MathTex` slipped in. Templates use
  `Text` only; `label_constructor=Text` covers coordinates.
- **No output found** = folder naming variance — recursive find,
  prefer `<Scene>.mp4` over `partial_movie_files` segments (section 10).
- **First render slow** = cold Python import. Expected; 150s timeout,
  hash cache makes it once per unique script.
- **`media/` appears in the wrong directory** = spawn `cwd` was the
  app root. Always a temp dir you own.
- **Raw expression executed** = validation skipped. Translate or
  reject; never interpolate (sections 2 + 8).
- **Two renders racing** = missing inFlight dedupe (section 11).
- **Autoplay blocked in a webview** = dropped `muted`/`controls`.
- **Exit 0 but no mp4** = looked in a predicted folder — section 10's
  recursive search with the `<Scene>.mp4` preference.
- **Garbled output in error strings** = ANSI not stripped; PowerShell
  also mangles redirected text encoding — capture child output as
  UTF-8 byte chunks, strip codes before matching.
- **Cache never hits** = hash input not byte-stable (e.g. object key
  order differs per request) — build the script from a canonical
  template before hashing.
