"""v0.3 analysis. Rule for repeated prompts: majority vote over all parsed answers for (model,prompt);
ties are dropped. Llama excluded. Reports FULL (427 pairs) and SCREENED (251 pairs) sets."""
import json, collections, warnings
import pandas as pd, numpy as np
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.stats import binomtest
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
raw=collections.defaultdict(list)
for f in ["results_p2_fast.jsonl","results_p2_strong.jsonl","results_p2_v2.jsonl"]:
    for l in open(f,encoding="utf8"):
        r=json.loads(l)
        if r["pred"] is not None and "llama" not in r["model"]: raw[(r["model"],r["prompt"])].append(r["pred"])
multi=[v for v in raw.values() if len(v)>1]; incons=[v for v in multi if len(set(v))>1]
import sys
TIE_RULE=sys.argv[1] if len(sys.argv)>1 else "drop"
resp={}; ties=0
for k,v in raw.items():
    c=collections.Counter(v).most_common()
    if len(c)>1 and c[0][1]==c[1][1]:
        ties+=1
        if TIE_RULE=="first": resp[k]=v[0]
        continue
    resp[k]=c[0][0]
print(f"prompts with >1 answer: {len(multi)}; inconsistent: {len(incons)} ({len(incons)/max(1,len(multi))*100:.1f}%); ties dropped: {ties}")
print("usable raw responses (5 models):",sum(len(v) for v in raw.values()))
items=json.load(open("items_p2.json",encoding="utf8"))+json.load(open("items_p2_v2.json",encoding="utf8"))
P=json.load(open("pairs.json",encoding="utf8")); EXCL=set(json.load(open("excluded_pids.json")))
SCR=set(json.load(open("screened_pids.json"))["screened_out"])
print("sources in 427 set:",collections.Counter(P[i]["src"] for i in range(len(P)) if i not in EXCL))
print("sources in 251 set:",collections.Counter(P[i]["src"] for i in range(len(P)) if i not in EXCL|SCR))
models=sorted({m for m,_ in resp})
rows=[dict(model=m.split("/")[1],pid=it["pid"],lang=it["lang"],cond=it["cond"],correct=int(resp[(m,it["prompt"])]==it["gold"]),pred=resp[(m,it["prompt"])])
      for m in models for it in items if (m,it["prompt"]) in resp and it["pid"] not in EXCL]
df=pd.DataFrame(rows)
print("\nyes-rate by model:",df.groupby("model").pred.apply(lambda s:round((s=='yes').mean(),3)).to_dict())
Wall=df.pivot_table(index=["model","pid","lang"],columns="cond",values="correct",aggfunc="first").reset_index()
Wall["known"]=(Wall.A==1)&(Wall.Arev==1); Wall["kp"]=Wall.known&(Wall.P==1)
def mcn(s,a,b):
    s=s[[a,b]].dropna(); x=int(((s[a]==1)&(s[b]==0)).sum()); y=int(((s[a]==0)&(s[b]==1)).sum())
    return x,y,(binomtest(y,x+y,.5).pvalue if x+y else float('nan'))
def rate(s,c): v=s[c].dropna(); return f"{v.mean()*100:.1f}% (n={len(v)})"
for NAME,W in [("FULL (427 pairs)",Wall),("SCREENED (251 pairs)",Wall[~Wall.pid.isin(SCR)])]:
    print("\n"+"="*70+"\n"+NAME, "units",len(W),"known",int(W.known.sum()),"known+P",int(W.kp.sum()))
    for lab,s in [("all",W),("known",W[W.known]),("known+P",W[W.kp])]:
        print(f"  {lab}: "+"  ".join(f"{c}={rate(s,c)}" for c in ["P","N","E","S","D","N_b","E_b","S_b","Erather","Epero"]))
    K=W[W.known]; KP=W[W.kp]
    fam={}
    x,y,p=mcn(K,"P","E"); fam["P_vs_E_known"]=p; print(f"  NON-CIRCULAR P vs E (known): P-right&E-wrong={x} E-right&P-wrong={y} p={p:.3g}")
    for L in ["en","es","fr"]:
        x,y,p=mcn(K[K.lang==L],"P","E"); print(f"     [{L}] {x} vs {y}")
    x,y,p=mcn(KP,"S","E"); fam["S_vs_E_knownP"]=p; print(f"  S vs E (known+P): S-right&E-wrong={x} E-right&S-wrong={y} p={p:.3g}")
    for L in ["en","es","fr"]:
        x,y,p=mcn(KP[KP.lang==L],"S","E"); fam[f"S_vs_E_{L}"]=p; print(f"     [{L}] {x} vs {y} p={p:.3g}")
    s=KP.dropna(subset=["E","E_b"])
    pat=collections.Counter(zip(s.E,s.E_b))
    print("  REVERSED QUESTION for E (known+P):",
          f"coherent correct(E yes,E_b no)={pat[(1,1)]}", f"literal-below(E no,E_b yes)={pat[(0,0)]}",
          f"'no' to both={pat[(0,1)]}", f"'yes' to both={pat[(1,0)]}", f"n={len(s)}")
    s2=KP.dropna(subset=["S","S_b"]); pat2=collections.Counter(zip(s2.S,s2.S_b)); print(f"     S coherent={pat2[(1,1)]}/{len(s2)}")
    en=KP[KP.lang=="en"]; x,y,p=mcn(en,"Erather","E"); fam["rather_vs_but"]=p
    print(f"  EN 'but rather' vs 'but' (known+P): rather-right&but-wrong={x} but-right&rather-wrong={y} p={p:.3g} | rather {rate(en,'Erather')} but {rate(en,'E')}")
    es=KP[KP.lang=="es"]; print(f"  ES (descriptive only) sino {rate(es,'E')} | concessive pero {rate(es,'Epero')}")
    rej,padj,_,_=multipletests(list(fam.values()),method="holm")
    print("  HOLM:",{k:f"{v:.3g}" for k,v in zip(fam,padj)})
    print("  E by model x lang (known+P):"); print(KP.pivot_table(index="model",columns="lang",values="E",aggfunc="mean").round(3).to_string())
    print("  by model (known+P):"); print(KP.groupby("model")[["P","N","E","S"]].mean().round(3).to_string())
    # common items: pairs known+P for all models
    cp=KP.groupby("pid").model.nunique(); common=cp[cp==len(models)].index
    C=KP[KP.pid.isin(common)]; print(f"  COMMON ITEMS (known+P for all {len(models)} models): {len(common)} pairs; E by model:",C.groupby("model").E.mean().round(3).to_dict())
    L_=KP.melt(id_vars=["model","pid","lang"],value_vars=["N","E","S"],var_name="cond",value_name="correct").dropna()
    L_["cond"]=pd.Categorical(L_.cond,["S","N","E"])
    m=smf.gee("correct ~ C(cond) + C(lang) + C(model)",groups="pid",data=L_,family=sm.families.Binomial(),cov_struct=sm.cov_struct.Exchangeable()).fit()
    ci=np.exp(m.conf_int()); t=pd.DataFrame({"OR":np.exp(m.params),"lo":ci[0],"hi":ci[1],"p":m.pvalues}).round(4)
    print("  GEE (known+P):"); print(t.loc[[i for i in t.index if "cond" in i or "lang" in i]].to_string())
