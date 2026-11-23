import os, json, random
import pandas as pd, numpy as np
random.seed(int(os.environ["SEED"])); rng=np.random.default_rng(int(os.environ["SEED"]))
df=pd.read_csv(os.environ["DATA"]); P=["mb","sk","ns","nb","nl","pe"]
df["y"]=df.month.str[:4].astype(int); df["m"]=df.month.str[5:].astype(int)
def shares(s): return s/s.sum()
rows=[]
for Y in sorted(df.y.unique()):
    prev=df[df.y==Y-1]; cur=df[df.y==Y]
    if prev.m.nunique()<12: continue
    fp=prev[prev.m.isin([10,11])]; fc=cur[cur.m.isin([10,11])]
    if len(fp)<2 or len(fc)<2: continue
    ann=shares(prev[P].sum()); fall=shares(fp[P].sum()); act=shares(fc[P].sum())
    rows.append((Y,((fall-act).abs()/act).mean(),((ann-act).abs()/act).mean()))
r=pd.DataFrame(rows,columns=["y","fall","ann"])
d=(r.fall-r.ann).values
bs=[rng.choice(d,len(d)).mean() for _ in range(5000)]
fm,am=r.fall.mean(),r.ann.mean()
print(json.dumps({"verdict":"survived" if fm<am else "falsified",
 "method":"for each year Y with full prior calendar year and Oct+Nov observed, predict Y fall shares of six-province fall total by prior-year fall shares vs prior-year annual shares; mean relative abs error across provinces, averaged over years; bootstrap over years for the difference",
 "years":r.y.tolist(),"fall_mre":fm,"annual_mre":am,"diff_mean":float(d.mean()),
 "years_fall_better":int((d<0).sum()),"n_years":len(d),"boot_diff_ci95":[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]}))
