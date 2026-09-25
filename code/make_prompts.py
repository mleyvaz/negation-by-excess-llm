import json
P=json.load(open("pairs.json",encoding="utf8"))
T={
"en":dict(N="It is not {x}.",E="It is not {x} but {y}.",S="It is not {x} but very {x}.",D="It is not {x} but {o}.",
          Q="Based only on this sentence, is it at least '{x}' (that is, {x} or more than {x})? Answer only Yes or No.",
          A="Is '{b}' a stronger degree of '{a}' (the same property, but more intense)? Answer only Yes or No."),
"es":dict(N="No es {x}.",E="No es {x}, sino {y}.",S="No es {x}, sino muy {x}.",D="No es {x}, sino {o}.",
          Q="Según solo esta oración, ¿es al menos '{x}' (es decir, {x} o más que {x})? Responde solo Sí o No.",
          A="¿Es '{b}' un grado más fuerte de '{a}' (la misma propiedad, pero más intensa)? Responde solo Sí o No."),
"fr":dict(N="Ce n'est pas {x}.",E="Ce n'est pas {x}, mais {y}.",S="Ce n'est pas {x}, mais très {x}.",D="Ce n'est pas {x}, mais {o}.",
          Q="D'après cette phrase uniquement, est-ce au moins « {x} » (c'est-à-dire {x} ou plus que {x}) ? Réponds seulement Oui ou Non.",
          A="« {b} » est-il un degré plus fort de « {a} » (la même propriété, mais plus intense) ? Réponds seulement Oui ou Non."),
}
items=[]
for i,p in enumerate(P):
    t=T[p["lang"]]; x,y,o=p["weak"],p["strong"],p["opp"]
    base=dict(pid=i,lang=p["lang"],weak=x,strong=y,opp=o,src=p["src"])
    items.append(dict(base,cond="A",prompt=t["A"].format(a=x,b=y),gold="yes"))
    items.append(dict(base,cond="Arev",prompt=t["A"].format(a=y,b=x),gold="no"))
    for c,g in (("N","no"),("E","yes"),("S","yes")):
        s=t[c].format(x=x,y=y); items.append(dict(base,cond=c,text=s,prompt=s+"\n"+t["Q"].format(x=x),gold=g))
    if o:
        s=t["D"].format(x=x,o=o); items.append(dict(base,cond="D",text=s,prompt=s+"\n"+t["Q"].format(x=x),gold="no"))
json.dump(items,open("items_p2.json","w",encoding="utf8"),ensure_ascii=False)
print(len(items)); [print(it["cond"],it["gold"],"|",it["prompt"].replace("\n"," || ")) for it in items[:6]]
