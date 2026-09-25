import os, json, re, sys, time, threading, concurrent.futures as cf, requests
MODELS=["meta-llama/llama-3.1-8b-instruct","mistralai/mistral-small-2603","openai/gpt-4o-mini",
        "openai/gpt-5.4-nano","google/gemini-3.1-flash-lite","qwen/qwen3.7-flash"]
KEY=os.environ["OPENROUTER_API_KEY"]; lock=threading.Lock()
which=sys.argv[1]
SEL={"fast":[m for m in MODELS if "mistral" not in m],"mistral":[m for m in MODELS if "mistral" in m],"strong":["openai/gpt-5.4-mini"],"v2":[m for m in MODELS if "mistral" not in m]+["openai/gpt-5.4-mini"]}[which]
out_f=f"results_p2_{which}.jsonl"
done=set()
if os.path.exists(out_f):
    for l in open(out_f,encoding="utf8"):
        r=json.loads(l)
        if r["pred"] is not None: done.add((r["model"],r["prompt"]))
out=open(out_f,"a",encoding="utf8")
def parse(t):
    t=re.sub(r"<think>.*?</think>","",(t or "").lower(),flags=re.S)
    m=re.search(r"\b(yes|no|sí|si|oui|non)\b",t)
    return None if not m else ("yes" if m.group(1) in ("yes","sí","si","oui") else "no")
def call(m,it):
    body={"model":m,"temperature":0,"max_tokens":3000,"reasoning":{"effort":"low"},"messages":[{"role":"user","content":it["prompt"]}]}
    err=""
    for a in range(6):
        try:
            j=requests.post("https://openrouter.ai/api/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=120).json()
            if "choices" not in j: err=str(j.get("error"))[:80]; time.sleep(4+6*a); continue
            txt=j["choices"][0]["message"].get("content") or ""; p=parse(txt)
            if p is None and a<2: err="empty"; continue
            r=dict(it,model=m,raw=txt[:200],pred=p); break
        except Exception as e: err=str(e)[:80]; time.sleep(4+6*a)
    else: r=dict(it,model=m,raw="ERROR:"+err,pred=None)
    with lock: out.write(json.dumps(r,ensure_ascii=False)+"\n"); out.flush()
items=json.load(open(sys.argv[2] if len(sys.argv)>2 else "items_p2.json",encoding="utf8"))
jobs=[(m,it) for it in items for m in SEL if (m,it["prompt"]) not in done]
print("jobs",len(jobs),flush=True)
with cf.ThreadPoolExecutor(1 if which=="mistral" else 20) as ex: list(ex.map(lambda a: call(*a), jobs))
print("finished",flush=True)
