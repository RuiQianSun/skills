import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
sh = S.groupby("year").comb_mpg.apply(lambda x: float((x >= 30).mean()))
slope = float(np.polyfit(sh.index, sh.values, 1)[0]) if len(sh) > 2 else float("nan")
out(len(sh) > 2 and bool((sh < 0.2).all()) and slope <= 0.01, years=len(sh), max_share=round(float(sh.max()), 4), slope_pp_per_year=round(slope * 100, 3))
