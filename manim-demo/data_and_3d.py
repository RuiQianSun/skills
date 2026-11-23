"""Manim demos: animated data visualization and a 3D surface.

Render (no LaTeX needed):
    manim -qm data_and_3d.py DataStory
    manim -qm data_and_3d.py Surface3D
"""
import numpy as np
from manim import *

# Sample data (synthetic): monthly values for three series.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SERIES = {
    "Alpha": np.array([22, 28, 35, 41, 52, 60, 63, 61, 66, 72, 78, 84]),
    "Beta": np.array([45, 52, 58, 61, 57, 50, 46, 44, 49, 55, 58, 61]),
    "Gamma": np.array([8, 10, 14, 20, 29, 41, 55, 68, 79, 88, 96, 104]),
}
COLORS = {"Alpha": BLUE, "Beta": ORANGE, "Gamma": GREEN}


def label(s, size=24, **kw):
    return Text(s, font_size=size, **kw)


class DataStory(Scene):
    def construct(self):
        title = label("Three series, one year (sample data)", 34).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.3))

        # Part 1: line chart drawn month by month with a moving cursor.
        ymax = 110
        ax = Axes(
            x_range=[0, 11, 1], y_range=[0, ymax, 20],
            x_length=7.6, y_length=4.6, tips=False,
            axis_config={"color": GREY_B},
        ).shift(LEFT * 1.2 + DOWN * 0.4)
        xt = VGroup(*[label(m, 18).next_to(ax.c2p(i, 0), DOWN, buff=0.15)
                      for i, m in enumerate(MONTHS)])
        yt = VGroup(*[label(str(v), 18).next_to(ax.c2p(0, v), LEFT, buff=0.15)
                      for v in range(0, ymax + 1, 20)])
        grid = VGroup(*[DashedLine(ax.c2p(0, v), ax.c2p(11, v), stroke_width=1,
                                   color=GREY_D) for v in range(20, ymax + 1, 20)])
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), Create(grid), run_time=1.2)

        t = ValueTracker(0)
        lines, dots, tags = VGroup(), VGroup(), VGroup()
        for name, ys in SERIES.items():
            c = COLORS[name]

            def make_line(ys=ys, c=c):
                end = t.get_value()
                xs = np.linspace(0, end, max(2, int(end * 12) + 2))
                pts = [ax.c2p(x, np.interp(x, range(12), ys)) for x in xs]
                return VMobject(stroke_color=c, stroke_width=4).set_points_smoothly(pts)

            line = always_redraw(make_line)
            dot = always_redraw(lambda ys=ys, c=c: Dot(
                ax.c2p(t.get_value(), np.interp(t.get_value(), range(12), ys)), color=c))
            row = list(SERIES).index(name)
            tag = always_redraw(lambda ys=ys, c=c, n=name, row=row: VGroup(
                Square(0.22, fill_color=c, fill_opacity=1, stroke_width=0),
                label(f"{n}  {np.interp(t.get_value(), range(12), ys):.0f}", 24, color=c),
            ).arrange(RIGHT, buff=0.2).move_to(ax.c2p(11, 0) + RIGHT * 0.6 + UP * (3.6 - row * 0.6),
                                              aligned_edge=LEFT))
            lines.add(line); dots.add(dot); tags.add(tag)
        self.add(lines, dots, tags)
        self.play(t.animate.set_value(11), run_time=6, rate_func=linear)
        self.wait(0.5)

        # Part 2: morph into a ranked bar chart of December totals.
        final = sorted(((n, ys[-1]) for n, ys in SERIES.items()), key=lambda p: -p[1])
        bars = VGroup()
        for i, (n, v) in enumerate(final):
            w = 7 * v / ymax
            bar = Rectangle(width=w, height=0.8, fill_color=COLORS[n], fill_opacity=0.9,
                            stroke_width=0)
            bar.move_to(LEFT * 3.5 + UP * (1 - i * 1.2), aligned_edge=LEFT)
            name = label(n, 26).next_to(bar, LEFT, buff=0.2)
            val = label(f"{v:.0f}", 26, color=COLORS[n]).next_to(bar, RIGHT, buff=0.2)
            bars.add(VGroup(bar, name, val))
        subtitle = label("December, ranked", 28, color=GREY_A).next_to(title, DOWN)
        self.play(FadeOut(VGroup(ax, xt, yt, grid, tags)),
                  *[ReplacementTransform(VGroup(lines[list(SERIES).index(n)],
                                                dots[list(SERIES).index(n)]), bars[i][0])
                    for i, (n, _) in enumerate(final)],
                  FadeIn(subtitle), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(b[1:], shift=RIGHT * 0.2) for b in bars], lag_ratio=0.3))
        self.play(Circumscribe(bars[0], color=YELLOW))
        self.wait(1.5)


class Surface3D(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], z_range=[-1.5, 1.5, 0.5],
                          x_length=7, y_length=7, z_length=4)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=0.85)

        title = label("z = 1.4 sin(1.6r - t) / (1 + r/2)", 30).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)

        phase = ValueTracker(0)

        def surf():
            p = phase.get_value()
            s = Surface(
                lambda u, v: axes.c2p(u, v, 1.4 * np.sin(np.hypot(u, v) * 1.6 - p) /
                                      (1 + np.hypot(u, v) / 2)),
                u_range=[-4, 4], v_range=[-4, 4], resolution=(32, 32),
                stroke_width=0.3, fill_opacity=1.0, stroke_color=BLACK,
            )
            s.set_fill_by_value(axes=axes, colorscale=[(PURPLE_E, -0.7), (BLUE_D, -0.25), (TEAL, 0.15), (YELLOW, 0.7)],
                                axis=2)
            return s

        surface = always_redraw(surf)
        self.play(Create(axes), FadeIn(title))
        self.add(surface)
        self.begin_ambient_camera_rotation(rate=0.35)
        self.play(phase.animate.set_value(2 * TAU), run_time=8, rate_func=linear)

        # Swing the camera overhead to show the contour pattern, then back.
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=5 * DEGREES, theta=-90 * DEGREES, zoom=0.65, run_time=2)
        self.wait(0.5)
        self.move_camera(phi=70 * DEGREES, theta=30 * DEGREES, zoom=1.0, run_time=2)
        self.wait(1)
