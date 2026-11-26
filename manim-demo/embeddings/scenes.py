"""ManimGL (3Blue1Brown's manim) scenes for the embedding explorer.

Render, with EMB_DIR pointing at the folder embed.py wrote:
    EMB_DIR=... manimgl scenes.py WordsAsVectors -w -m
Every number shown comes from the all-MiniLM-L6-v2 vectors in EMB_DIR.
"""
import json
import os

import numpy as np
from manimlib import *

EMB = os.environ["EMB_DIR"]
DATA = json.load(open(os.path.join(EMB, "projector.json")))
V = np.load(os.path.join(EMB, "vectors.npy"))
Q = np.load(os.path.join(EMB, "qvectors.npy"))
ITEMS = DATA["items"]
WORD = {it["label"]: i for i, it in enumerate(ITEMS) if it["kind"] == "word"}
GROUPS = list(dict.fromkeys(it["group"] for it in ITEMS if it["kind"] == "word"))
TOPICS = list(dict.fromkeys(it["group"] for it in ITEMS if it["kind"] == "passage"))
PALETTE = ["#5B8DEF", "#F08A4B", "#3DB389", "#C46BD9", "#E2B43B", "#4FC1D9", "#E5677D",
           "#8F9BF2", "#9BC53D", "#D98E5B", "#7FA7B5"]
TOPIC_COLORS = ["#C9853B", "#E2B43B", "#5B8DEF", "#3DB389"]
INK = "#E8E6E3"
MUTED = "#8B8F98"


def nearest(v, pool, skip=(), k=1):
    sims = V[pool] @ v
    order = [pool[j] for j in np.argsort(-sims) if ITEMS[pool[j]]["label"] not in skip]
    return [(ITEMS[i]["label"], float(V[i] @ v)) for i in order[:k]]


def label(text, size=28, color=INK):
    return Text(text, font_size=size, font="Inter").set_color(color)


class WordsAsVectors(Scene):
    def construct(self):
        title = label("Words become vectors", 44).to_edge(UP)
        self.play(Write(title))

        nums = ", ".join(f"{x:+.2f}" for x in V[WORD["king"]][:5])
        row = VGroup(label("king", 36, YELLOW), label("→", 36), label(f"[{nums}, … ]", 30, MUTED)).arrange(RIGHT)
        sub = label("384 numbers from a trained model (all-MiniLM-L6-v2)", 24, MUTED).next_to(row, DOWN)
        self.play(FadeIn(row, shift=UP * 0.3), FadeIn(sub))
        self.wait(1.2)
        self.play(FadeOut(row), FadeOut(sub))

        names = ["man", "woman", "king", "queen"]
        M = np.array([V[WORD[n]] for n in names])
        c = M.mean(0)
        # Axes: the "gender" and "royalty" directions the model learned, from these four words.
        gx = (M[1] - M[0]) + (M[3] - M[2])
        gx /= np.linalg.norm(gx)
        ry = (M[2] - M[0]) + (M[3] - M[1])
        ry -= (ry @ gx) * gx
        ry /= np.linalg.norm(ry)
        xy = np.stack([(M - c) @ gx, (M - c) @ ry], 1)
        xy = xy / np.abs(xy).max(0) * np.array([2.8, 1.6])
        pts = {n: np.array([xy[i, 0], xy[i, 1] - 0.5, 0]) for i, n in enumerate(names)}
        axes_note = VGroup(label("→ the model's 'female' direction", 20, MUTED), label("↑ the model's 'royal' direction", 20, MUTED)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.08).to_corner(UL).shift(DOWN * 0.9)
        colors = {"man": BLUE, "woman": TEAL, "king": YELLOW, "queen": PINK}
        dots = {n: Dot(pts[n], radius=0.09).set_color(colors[n]) for n in names}
        tags = {n: label(n, 30, colors[n]).next_to(dots[n], DOWN if n in ("man", "woman", "queen") else UP, buff=0.15) for n in names}
        note = label("Four of those vectors, flattened onto two directions they share", 24, MUTED).to_edge(DOWN)
        self.play(*[GrowFromCenter(dots[n]) for n in names], *[FadeIn(tags[n]) for n in names], FadeIn(note), FadeIn(axes_note))
        self.wait(0.6)

        a1 = Arrow(pts["man"], pts["woman"], buff=0.12).set_color(TEAL)
        t1 = label("woman − man", 22, TEAL).next_to(a1, DOWN, buff=0.45)
        self.play(GrowArrow(a1), FadeIn(t1))
        a2 = a1.copy()
        self.play(a2.animate.shift(pts["king"] - pts["man"]), run_time=1.4)
        t2 = label("king − man + woman", 22, YELLOW).next_to(a2.get_end(), UP, buff=0.2)
        self.play(FadeIn(t2))

        v = V[WORD["king"]] - V[WORD["man"]] + V[WORD["woman"]]
        v /= np.linalg.norm(v)
        (best, sim), = nearest(v, list(WORD.values()), skip=("king", "man", "woman"))
        res = label(f"Nearest word to king − man + woman: {best}  (cosine {sim:.2f})", 28, PINK)
        link = DashedLine(a2.get_end(), dots["queen"].get_center()).set_stroke(PINK, 2)
        self.play(ShowCreation(link), FadeOut(note), Write(res.to_edge(DOWN)))
        self.play(Indicate(dots["queen"], scale_factor=1.8, color=PINK))
        self.wait(1.5)


class WordCloud3D(Scene):
    def construct(self):
        frame = self.frame
        frame.reorient(-30, 70)
        idx = [WORD[w] for w in WORD]
        P = np.array(DATA["tsne"])[idx] * 3.2
        clouds = Group()
        for g, gname in enumerate(GROUPS):
            sel = [k for k, i in enumerate(idx) if ITEMS[i]["group"] == gname]
            cloud = DotCloud(P[sel], radius=0.06).set_color(PALETTE[g % len(PALETTE)])
            clouds.add(cloud)
        title = label("240 words, 384 dimensions, squeezed into 3", 36).to_edge(UP).fix_in_frame()
        sub = label("t-SNE keeps neighbors near each other; color is the word's group", 22, MUTED).next_to(title, DOWN).fix_in_frame()
        self.play(Write(title), FadeIn(sub))
        self.play(LaggedStartMap(FadeIn, clouds, lag_ratio=0.15), run_time=2.5)
        tags = Group()
        for w in ["king", "queen", "dog", "puppy", "coffee", "tea", "Paris", "Tokyo", "rain", "happy", "train", "doctor"]:
            k = idx.index(WORD[w])
            base = label(w, 22)
            pos = P[k] + np.array([0, 0, 0.22])
            t = base.copy()
            t.add_updater(lambda m, base=base, pos=pos: m.become(
                base.copy().rotate(PI / 2, RIGHT).rotate(frame.get_euler_angles()[0], OUT).move_to(pos)))
            tags.add(t)
        self.play(FadeIn(tags))
        frame.add_updater(lambda m, dt: m.increment_theta(-0.25 * dt))
        self.wait(8)
        frame.clear_updaters()


class CosineSimilarity(Scene):
    def construct(self):
        title = label("Similar meaning, similar direction", 42).to_edge(UP)
        self.play(Write(title))
        origin = LEFT * 3.2 + DOWN * 1.6
        r = 3.2
        ang = ValueTracker(70 * DEGREES)
        a = Arrow(origin, origin + r * RIGHT, buff=0).set_color(BLUE)
        ta = label("dog", 28, BLUE).next_to(a.get_end(), RIGHT, buff=0.15)

        def tip():
            return origin + r * np.array([np.cos(ang.get_value()), np.sin(ang.get_value()), 0])

        b = always_redraw(lambda: Arrow(origin, tip(), buff=0).set_color(YELLOW))
        arc = always_redraw(lambda: Arc(0, ang.get_value(), radius=0.8, arc_center=origin).set_color(MUTED))
        readout = always_redraw(lambda: label(f"cos θ = {np.cos(ang.get_value()):.2f}", 34, YELLOW).move_to(RIGHT * 3.4 + UP * 1.4))
        formula = label("cos θ = (a · b) / (|a| |b|)", 26, MUTED).move_to(RIGHT * 3.4 + UP * 0.6)
        self.play(GrowArrow(a), FadeIn(ta), FadeIn(b), FadeIn(arc), FadeIn(readout), FadeIn(formula))
        self.play(ang.animate.set_value(10 * DEGREES), run_time=1.8)
        self.play(ang.animate.set_value(150 * DEGREES), run_time=2.2)
        self.play(ang.animate.set_value(np.arccos(float(V[WORD["dog"]] @ V[WORD["puppy"]]))), run_time=1.5)

        rows = VGroup()
        for w in ["puppy", "cat", "wolf", "pizza", "taxi"]:
            s = float(V[WORD["dog"]] @ V[WORD[w]])
            rows.add(VGroup(label(f"dog · {w}", 26), label(f"{s:.2f}", 26, YELLOW)).arrange(RIGHT, buff=0.6))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.4 + DOWN * 1.2)
        self.play(LaggedStartMap(FadeIn, rows, shift=LEFT * 0.2, lag_ratio=0.2), run_time=2)
        note = label("Real cosines from the model: vectors are unit length, so cosine is the dot product", 20, MUTED).to_edge(DOWN)
        self.play(FadeIn(note))
        self.wait(2)


class RagPipeline(Scene):
    def construct(self):
        qi = next(i for i, q in enumerate(DATA["questions"]) if q["label"].startswith("Why is Venus"))
        qtext = DATA["questions"][qi]["label"]
        qv = Q[qi]
        pidx = [i for i, it in enumerate(ITEMS) if it["kind"] == "passage"]

        title = label("Retrieval-augmented generation", 42).to_edge(UP)
        self.play(Write(title))
        q = label(f"“{qtext}”", 28, YELLOW).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(q, shift=DOWN * 0.2))

        X = V[pidx]
        mu = X.mean(0)
        _, _, vt = np.linalg.svd(X - mu, full_matrices=False)
        XY = (X - mu) @ vt[:2].T
        qxy = (qv - mu) @ vt[:2].T
        sc = 2.1 / np.abs(XY).max()
        center = LEFT * 2.6 + DOWN * 0.9
        to3 = lambda p: center + np.array([p[0] * sc, p[1] * sc, 0])
        box = SurroundingRectangle(VGroup(*[Dot(to3(p)) for p in XY]), buff=0.35).set_stroke(MUTED, 1)
        cap = label("40 passages, embedded once and stored", 20, MUTED).next_to(box, DOWN, buff=0.15)
        dots = VGroup()
        for k, i in enumerate(pidx):
            dots.add(Dot(to3(XY[k]), radius=0.07).set_color(TOPIC_COLORS[TOPICS.index(ITEMS[i]["group"])]))
        legend = VGroup(*[VGroup(Dot(radius=0.06).set_color(TOPIC_COLORS[t]), label(name, 18, MUTED)).arrange(RIGHT, buff=0.12)
                          for t, name in enumerate(TOPICS)]).arrange(RIGHT, buff=0.35).next_to(box, UP, buff=0.15)
        self.play(ShowCreation(box), LaggedStartMap(GrowFromCenter, dots, lag_ratio=0.03), FadeIn(cap), FadeIn(legend), run_time=2)

        qdot = Dot(to3(qxy), radius=0.11).set_color(YELLOW)
        self.play(TransformFromCopy(q, qdot), run_time=1.2)
        sims = X @ qv
        top = np.argsort(-sims)[:3]
        lines = VGroup(*[DashedLine(qdot.get_center(), dots[k].get_center()).set_stroke(YELLOW, 2) for k in top])
        self.play(ShowCreation(lines), *[dots[k].animate.scale(1.8) for k in top], run_time=1.2)

        picks = VGroup()
        for rank, k in enumerate(top):
            it = ITEMS[pidx[k]]
            picks.add(VGroup(label(f"{rank + 1}. {it['label']}", 22), label(f"{sims[k]:.2f}", 22, YELLOW)).arrange(RIGHT, buff=0.4))
        picks.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        head = label("Top 3 by cosine similarity", 22, MUTED)
        panel = VGroup(head, picks).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 2.9 + UP * 0.3)
        self.play(FadeIn(head), LaggedStartMap(FadeIn, picks, shift=LEFT * 0.2, lag_ratio=0.25))

        prompt = VGroup(label("Prompt to the language model", 20, MUTED),
                        label("Context: passages 1 to 3", 22), label("Question: " + qtext, 18, YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        frame_box = SurroundingRectangle(prompt, buff=0.2).set_stroke(TEAL, 2)
        grp = VGroup(frame_box, prompt).next_to(panel, DOWN, buff=0.5).align_to(panel, LEFT)
        arrow = Arrow(panel.get_bottom(), grp.get_top(), buff=0.08).set_color(TEAL)
        self.play(GrowArrow(arrow), FadeIn(grp, shift=DOWN * 0.2))
        out = label("The answer draws on the retrieved text", 22, TEAL).next_to(grp, DOWN, buff=0.3).align_to(grp, LEFT)
        self.play(Write(out))
        self.wait(2)
