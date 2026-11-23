from manim import *

N = 6
S = 0.55  # square side
COLORS = [BLUE, TEAL, GREEN, YELLOW, ORANGE, RED]


class OddSquares(Scene):
    def construct(self):
        title = Text("Adding odd numbers makes squares", font_size=40).to_edge(UP)
        self.play(Write(title))

        origin = LEFT * 5.6 + DOWN * 2.0
        grid = VGroup()
        terms = []
        total = 0

        eq = Text("", font_size=34)
        eq.to_edge(RIGHT, buff=0.8).shift(UP * 0.5)
        self.add(eq)

        for k in range(N):
            odd = 2 * k + 1
            total += odd
            # L-shaped layer k: column x=k (rows 0..k) plus row y=k (cols 0..k-1)
            cells = [(k, y) for y in range(k + 1)] + [(x, k) for x in range(k)]
            layer = VGroup(*[
                Square(S, stroke_width=2, stroke_color=WHITE,
                       fill_color=COLORS[k], fill_opacity=0.85)
                .move_to(origin + RIGHT * (x * S + S / 2) + UP * (y * S + S / 2))
                for x, y in cells
            ])
            terms.append(str(odd))

            new_eq = VGroup(
                Text(" + ".join(terms), font_size=34),
                Text(f"= {total} = {k + 1} × {k + 1}", font_size=34, color=COLORS[k]),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            new_eq.move_to(UP * 0.6).align_to(LEFT * -0.4, LEFT)

            label = Text(f"+{odd}", font_size=28, color=COLORS[k]).next_to(layer, UR, buff=0.1)

            run = 0.9 if k < 3 else 0.6
            self.play(
                LaggedStart(*[GrowFromCenter(c) for c in layer], lag_ratio=0.08),
                FadeIn(label, shift=DOWN * 0.2),
                Transform(eq, new_eq),
                run_time=run + 0.3,
            )
            self.play(FadeOut(label), run_time=0.3)
            grid.add(layer)

        brace_b = Brace(grid, DOWN)
        brace_l = Brace(grid, LEFT)
        nb = Text("n", font_size=32, slant=ITALIC).next_to(brace_b, DOWN, buff=0.1)
        nl = Text("n", font_size=32, slant=ITALIC).next_to(brace_l, LEFT, buff=0.1)
        self.play(GrowFromCenter(brace_b), GrowFromCenter(brace_l), FadeIn(nb), FadeIn(nl))

        general = Text("1 + 3 + 5 + … + (2n − 1) = n²", font_size=38, color=YELLOW)
        general.scale_to_fit_width(min(general.width, 6.2))
        general.next_to(eq, DOWN, buff=0.8).align_to(eq, LEFT)
        box = SurroundingRectangle(general, color=YELLOW, buff=0.2)
        self.play(Write(general), run_time=1.5)
        self.play(Create(box))
        self.play(Indicate(grid, scale_factor=1.05, color=WHITE))
        self.wait(2)
