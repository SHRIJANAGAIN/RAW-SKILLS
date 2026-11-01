"""Install smoke test for the Manim video pipeline.

    python -m manim render -ql examples/plot_scene.py MyScene

Renders media/videos/.../MyScene.mp4 (480p15, a few MB, ~5-10s after the
first render). White background, Pango Text everywhere - no LaTeX needed.
"""

from manim import *
import numpy as np

config.background_color = "#ffffff"

INK = "#0f172a"
BLUE = "#0437f2"
RED = "#e11d48"
MUTED = "#94a3b8"


def _step(span, target=5.0):
    """Nice axis ticks: 1 / 2 / 5 x 10^n."""
    raw = max(abs(span), 1e-9) / target
    mag = 10.0 ** np.floor(np.log10(raw))
    norm = raw / mag
    unit = 1.0 if norm < 1.5 else 2.0 if norm < 3 else 5.0 if norm < 7 else 10.0
    return unit * mag


def _sample(fn, x0, x1):
    """Pick the y-window from the curve itself."""
    with np.errstate(all="ignore"):
        vals = np.array([fn(float(t)) for t in np.linspace(x0, x1, 400)])
    vals = vals[np.isfinite(vals)]
    smin, smax = (float(vals.min()), float(vals.max())) if vals.size else (-1.0, 1.0)
    span = max(smax - smin, 1e-9)
    return smin - 0.18 * span, smax + 0.18 * span


class MyScene(Scene):
    def construct(self):
        f = lambda x: np.sin(x)
        x0, x1 = -6.28, 6.28
        ylo, yhi = _sample(f, x0, x1)
        ylo, yhi = min(ylo, 0.0), max(yhi, 0.0)

        axes = Axes(
            x_range=[x0, x1, _step(x1 - x0)],
            y_range=[ylo, yhi, _step(yhi - ylo)],
            x_length=10.0,
            y_length=5.4,
            tips=True,
            axis_config={"color": MUTED, "stroke_width": 2},
        )
        axes.add_coordinates(label_constructor=Text)

        title = Text("y = sin(x)", font_size=26, color=INK).to_edge(UP, buff=0.2)
        self.play(Create(axes), run_time=0.7)
        self.play(Write(title), run_time=0.5)

        curve = axes.plot(f, color=BLUE, use_smoothing=True)
        self.play(Create(curve), run_time=2.0)

        for px, plabel in [(1.57, "max"), (-1.57, "min")]:
            py = float(f(px))
            dot = Dot(axes.c2p(px, py), color=RED, radius=0.07)
            lab = Text(plabel, font_size=20, color=RED).next_to(dot, UP, buff=0.16)
            self.play(FadeIn(dot, scale=0.4), Write(lab), run_time=0.45)

        self.wait(0.8)
