"""Build Paper-2 items from human-validated scalar datasets (EN/ES/FR)."""
import glob, os, itertools, random, json
random.seed(20260925)
DIRS={"en":["scalar_adjs/data/demelo","scalar_adjs/data/crowd","scalar_adjs/data/wilkinson"],
      "es":["scalar_adjs/multilingual_data/es/demelo","scalar_adjs/multilingual_data/es/wilkinson"],
      "fr":["scalar_adjs/multilingual_data/fr/demelo","scalar_adjs/multilingual_data/fr/wilkinson"]}
def load(f):
    lv=[]
    for line in open(f,encoding="utf8"):
        if "\t" in line:
            r,w=line.rstrip("\n").split("\t",1); lv.append((int(r),[x.strip() for x in w.split("||") if x.strip()]))
    return sorted(lv)
def opposite_file(f):
    b=os.path.basename(f).replace(".rankings","")
    o = b[2:]+"XX" if b.startswith("XX") else "XX"+b[:-2]
    return os.path.join(os.path.dirname(f), o+".rankings")
single=lambda w: " " not in w and "-" not in w
items=[]
for lang,dirs in DIRS.items():
    pool=[]
    for d in dirs:
        for f in glob.glob(d+"/gold_rankings/*.rankings"):
            lv=load(f); of=opposite_file(f)
            opp=None
            if os.path.exists(of):
                olv=load(of); cand=[w for w in olv[0][1] if single(w)] if olv else []
                opp=cand[0] if cand else None
            per=[]
            for (r1,w1),(r2,w2) in itertools.combinations(lv,2):
                if r2<=r1: continue
                for x in w1:
                    for y in w2:
                        if single(x) and single(y) and x!=y: per.append((x,y))
            random.shuffle(per)
            for x,y in per[:3]:
                pool.append(dict(lang=lang,src=os.path.basename(d),scale=os.path.basename(f),weak=x,strong=y,opp=opp))
    # dedupe and sample 150
    seen=set(); uniq=[]
    for p in pool:
        k=(p["weak"],p["strong"])
        if k not in seen: seen.add(k); uniq.append(p)
    random.shuffle(uniq); items+=uniq[:150]
    print(lang,"pool",len(uniq),"sampled",min(150,len(uniq)),"with antonym",sum(1 for p in uniq[:150] if p["opp"]))
json.dump(items,open("pairs.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
for p in items[:3]+items[150:153]+items[300:303]: print(p["lang"],p["weak"],"<",p["strong"],"| opp:",p["opp"])
