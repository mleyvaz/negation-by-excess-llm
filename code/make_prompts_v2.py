"""Extra controls requested by the referee (v0.2)."""
import json
P=json.load(open("pairs.json",encoding="utf8"))
Q={"en":"Based only on this sentence, is it at least '{x}' (that is, {x} or more than {x})? Answer only Yes or No.",
   "es":"Según solo esta oración, ¿es al menos '{x}' (es decir, {x} o más que {x})? Responde solo Sí o No.",
   "fr":"D'après cette phrase uniquement, est-ce au moins « {x} » (c'est-à-dire {x} ou plus que {x}) ? Réponds seulement Oui ou Non."}
QB={"en":"Based only on this sentence, is it less than '{x}' (below the level {x})? Answer only Yes or No.",
    "es":"Según solo esta oración, ¿es menos que '{x}' (por debajo del nivel {x})? Responde solo Sí o No.",
    "fr":"D'après cette phrase uniquement, est-ce moins que « {x} » (en dessous du niveau {x}) ? Réponds seulement Oui ou Non."}
POS={"en":"It is {y}.","es":"Es {y}.","fr":"C'est {y}."}
E={"en":"It is not {x} but {y}.","es":"No es {x}, sino {y}.","fr":"Ce n'est pas {x}, mais {y}."}
S={"en":"It is not {x} but very {x}.","es":"No es {x}, sino muy {x}.","fr":"Ce n'est pas {x}, mais très {x}."}
N={"en":"It is not {x}.","es":"No es {x}.","fr":"Ce n'est pas {x}."}
ALT={"en":("Erather","It is not {x} but rather {y}."),"es":("Epero","No es {x}, pero {y}.")}
items=[]
for i,p in enumerate(P):
    L,x,y=p["lang"],p["weak"],p["strong"]; base=dict(pid=i,lang=L,weak=x,strong=y,opp=p["opp"],src=p["src"])
    s=POS[L].format(y=y); items.append(dict(base,cond="P",text=s,prompt=s+"\n"+Q[L].format(x=x),gold="yes"))   # affirmative entailment control
    for c,tpl,g in (("N_b",N[L],"yes"),("E_b",E[L],"no"),("S_b",S[L],"no")):                                   # reversed question (below X?)
        s=tpl.format(x=x,y=y); items.append(dict(base,cond=c,text=s,prompt=s+"\n"+QB[L].format(x=x),gold=g))
    if L in ALT:                                                                                             # conjunction contrast within language
        c,tpl=ALT[L]; s=tpl.format(x=x,y=y); items.append(dict(base,cond=c,text=s,prompt=s+"\n"+Q[L].format(x=x),gold="yes"))
json.dump(items,open("items_p2_v2.json","w",encoding="utf8"),ensure_ascii=False)
from collections import Counter; print(len(items),Counter(i["cond"] for i in items))
