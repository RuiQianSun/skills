"""Embed words, passages and questions with all-MiniLM-L6-v2 (ONNX), then project.

Usage: python embed.py <model_dir> <out_dir>
Writes projector.json: labels, kinds, groups, int8-quantized 384-d unit vectors,
3D PCA and 3D t-SNE coordinates, and the PCA basis so new points can be placed.
"""
import base64
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from tokenizers import Tokenizer

from corpus import WORDS, PASSAGES, QUESTIONS

model_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
tok.enable_padding(pad_id=0, pad_token="[PAD]")
tok.enable_truncation(max_length=256)
sess = ort.InferenceSession(str(model_dir / "model.onnx"), providers=["CPUExecutionProvider"])


def embed(texts, batch=64):
    out = []
    for i in range(0, len(texts), batch):
        enc = tok.encode_batch(texts[i:i + batch])
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        feeds = {"input_ids": ids, "attention_mask": mask, "token_type_ids": np.zeros_like(ids)}
        hidden = sess.run(None, {k: v for k, v in feeds.items() if k in {i.name for i in sess.get_inputs()}})[0]
        m = mask[..., None].astype(np.float32)
        vec = (hidden * m).sum(1) / m.sum(1)
        out.append(vec / np.linalg.norm(vec, axis=1, keepdims=True))
    return np.vstack(out)


items = []
for group, words in WORDS.items():
    for w in words:
        items.append({"label": w, "kind": "word", "group": group, "text": w})
for topic, chunks in PASSAGES.items():
    for j, (title, text) in enumerate(chunks):
        items.append({"label": title, "kind": "passage", "group": topic, "text": text})
questions = [{"label": q, "kind": "question", "group": t, "text": q} for t, q in QUESTIONS]

V = embed([it["text"] for it in items])
Q = embed([q["text"] for q in questions])

pca = PCA(n_components=3, random_state=0).fit(V)
P = pca.transform(V)
T = TSNE(n_components=3, perplexity=18, init="pca", random_state=0, max_iter=1500).fit_transform(V)


def norm(a):
    a = a - a.mean(0)
    return a / np.abs(a).max()


def q8(M):
    return base64.b64encode(np.clip(np.round(M * 127), -127, 127).astype(np.int8).tobytes()).decode()


data = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "dims": int(V.shape[1]),
    "items": [{k: it[k] for k in ("label", "kind", "group", "text")} for it in items],
    "vectors_int8": q8(V),
    "pca": np.round(norm(P), 4).tolist(),
    "pca_variance": [round(float(x), 4) for x in pca.explained_variance_ratio_],
    "pca_mean": np.round(pca.mean_, 5).tolist(),
    "pca_components": np.round(pca.components_, 5).tolist(),
    "pca_scale": float(np.abs(P - P.mean(0)).max()),
    "pca_center": np.round(P.mean(0), 5).tolist(),
    "tsne": np.round(norm(T), 4).tolist(),
    "questions": [{**q, "vector_int8": q8(Q[i:i + 1])} for i, q in enumerate(questions)],
}
(out_dir / "projector.json").write_text(json.dumps(data, separators=(",", ":")))
np.save(out_dir / "vectors.npy", V)
np.save(out_dir / "qvectors.npy", Q)
print(len(items), "points,", len(questions), "questions, PCA var", data["pca_variance"])
