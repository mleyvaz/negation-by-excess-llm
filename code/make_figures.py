"""Figures for Paper 2. Every value is parsed from results_p2_v4.txt (output of analyze_p2_v3.py);
nothing is typed by hand. Output: fig1_conditions.(png|pdf), fig2_errors_marking.(png|pdf), 600 dpi."""
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

txt = open("results_p2_v4.txt", encoding="utf8").read()
full = txt.split("SCREENED")[0]
scr = txt.split("SCREENED")[1]

def pooled(block):
    line = re.search(r"known\+P: (.*)", block).group(1)
    return {c: (float(p) / 100, int(n)) for c, p, n in re.findall(r"(\w+)=([\d.]+)% \(n=(\d+)\)", line)}

def by_model(block):
    sec = block.split("by model (known+P):")[1].split("COMMON")[0].strip().splitlines()
    cols = sec[0].split()[1:]
    out = {}
    for ln in sec[2:]:
        parts = ln.split()
        out[parts[0]] = dict(zip(cols, map(float, parts[1:])))
    return out

def reversed_q(block):
    m = re.search(r"coherent correct\(E yes,E_b no\)=(\d+) literal-below\(E no,E_b yes\)=(\d+) 'no' to both=(\d+) 'yes' to both=(\d+) n=(\d+)", block)
    return list(map(int, m.groups()))

def rather(block):
    m = re.search(r"rather-right&but-wrong=(\d+) but-right&rather-wrong=(\d+).*?rather ([\d.]+)% \(n=(\d+)\) but ([\d.]+)% \(n=(\d+)\)", block)
    g = m.groups()
    return int(g[0]), int(g[1]), float(g[2]) / 100, int(g[3]), float(g[4]) / 100, int(g[5])

NAMES = {"gemini-3.1-flash-lite": "Gemini 3.1 Flash-Lite", "gpt-4o-mini": "GPT-4o-mini",
         "gpt-5.4-mini": "GPT-5.4-mini", "gpt-5.4-nano": "GPT-5.4-nano", "qwen3.7-flash": "Qwen 3.7 Flash"}
MARK = ["o", "s", "D", "^", "v"]
COL = {"full": "#1b4f72", "scr": "#7fb3d5", "E": "#c0392b"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.linewidth": 0.7, "xtick.major.width": 0.7,
                     "ytick.major.width": 0.7, "legend.frameon": False, "savefig.dpi": 600})

# ---------- Figure 1 ----------
pf, ps = pooled(full), pooled(scr)
conds = ["P", "N", "S", "D", "E"]
labels = {"P": "P\ndark", "N": "N\nnot dim", "S": "S\nnot dim,\nvery dim",
          "D": "D\nnot dim,\n[antonym]", "E": "E\nnot dim,\ndark"}
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.25, 1]})
x = np.arange(len(conds)); w = 0.36
for off, d, key, lab in [(-w / 2, pf, "full", "Full set (427 pairs)"), (w / 2, ps, "scr", "Screened set (247 pairs)")]:
    p = np.array([d[c][0] for c in conds]); n = np.array([d[c][1] for c in conds])
    lo, hi = proportion_confint(np.round(p * n), n, method="wilson")
    colors = [COL[key]] * 4 + [COL["E"] if key == "full" else "#e6b0aa"]
    a.bar(x + off, p * 100, w, color=colors, edgecolor="white", linewidth=0.5, label=lab)
    a.errorbar(x + off, p * 100, yerr=[(p - lo) * 100, (hi - p) * 100], fmt="none", ecolor="black", elinewidth=0.7, capsize=2)
for i, c in enumerate(conds):
    for off, d in [(-w / 2, pf), (w / 2, ps)]:
        p_, n_ = d[c]; hi_ = proportion_confint(round(p_ * n_), n_, method="wilson")[1]
        a.text(i + off, hi_ * 100 + 1.2, f"{p_*100:.0f}", ha="center", va="bottom", fontsize=6)
a.set_xticks(x); a.set_xticklabels([labels[c] for c in conds], fontsize=6.8)
a.set_ylim(0, 108); a.set_yticks(range(0, 101, 20)); a.set_ylabel('% correct on "is it at least dim?"')
a.set_title("(a) Accuracy by condition, known+P units", loc="left", fontsize=8.5, fontweight="bold")
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=2, fontsize=6.8)

bm = by_model(full)
mc = ["N", "S", "E"]
for k, (m, vals) in enumerate(bm.items()):
    y = [vals[c] * 100 for c in mc]
    b.plot(range(3), y, marker=MARK[k], ms=4.5, lw=0.9, color=plt.cm.viridis(k / 4.5), label=NAMES[m])
b.set_xticks(range(3)); b.set_xticklabels(["N\nplain negation", "S\nsame-word\ncorrective", "E\nlexical\ncorrective"], fontsize=7)
b.set_ylim(0, 105); b.set_yticks(range(0, 101, 20)); b.set_xlim(-0.3, 2.3)
b.set_title("(b) By model, known+P units", loc="left", fontsize=8.5, fontweight="bold")
b.legend(loc="lower left", fontsize=6.5, handlelength=1.8)
fig.tight_layout(w_pad=2.2)
for ext in ("png", "pdf"):
    fig.savefig(f"fig1_conditions.{ext}", bbox_inches="tight")

# ---------- Figure 2 ----------
rf, rs = reversed_q(full), reversed_q(scr)
cats = ["Coherent and correct", "Literal reading", '"No" to both', '"Yes" to both']
ccol = ["#1e8449", "#c0392b", "#7f8c8d", "#d4ac0d"]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.7, 1]})
for row, (vals, name) in enumerate([(rf, "Full set"), (rs, "Screened set")]):
    n = vals[4]; left = 0
    for v, c, lab in zip(vals[:4], ccol, cats):
        share = v / n * 100
        a.barh(row, share, left=left, color=c, edgecolor="white", height=0.55, label=lab if row == 0 else None)
        if share > 8:
            a.text(left + share / 2, row, f"{share:.0f}%\n({v})", ha="center", va="center", fontsize=6.5, color="white")
        else:
            a.text(left + share / 2, row - 0.31, f"{share:.0f}% ({v})", ha="center", va="bottom", fontsize=5.8)
        left += share
    a.text(102, row, f"n = {n}", va="center", fontsize=6.8)
a.set_yticks([0, 1]); a.set_yticklabels(["Full set", "Screened set"]); a.invert_yaxis()
a.set_xlim(0, 116); a.set_xticks(range(0, 101, 25)); a.set_xlabel("% of known+P units")
a.set_title("(a) Lexical corrective E: reversed question", loc="left", fontsize=8.5, fontweight="bold")
a.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.47, -0.32), fontsize=6.5, handlelength=1.2, columnspacing=1.0)

rr, bb, pr, nr, pb, nb = rather(full)
lo, hi = proportion_confint(np.round(np.array([pb, pr]) * nb), nb, method="wilson")
vals = np.array([pb, pr]) * 100
b.bar([0, 1], vals, 0.55, color=["#e6b0aa", COL["E"]], edgecolor="white")
b.errorbar([0, 1], vals, yerr=[vals - lo * 100, hi * 100 - vals], fmt="none", ecolor="black", elinewidth=0.7, capsize=2.5)
for i, v in enumerate(vals):
    b.text(i, hi[i] * 100 + 2, f"{v:.1f}%", ha="center", fontsize=7)
b.set_xticks([0, 1]); b.set_xticklabels(['"not dim\nbut dark"', '"not dim but\nrather dark"'], fontsize=7)
b.set_ylim(0, 75); b.set_ylabel("% correct, English")
b.set_title(f"(b) Explicit marking (n = {nb})", loc="left", fontsize=8.5, fontweight="bold")
b.text(0.5, 67, f"discordant pairs {rr} vs {bb}", ha="center", fontsize=6.5, style="italic")
fig.tight_layout(w_pad=3.5)
for ext in ("png", "pdf"):
    fig.savefig(f"fig2_errors_marking.{ext}", bbox_inches="tight")
print("ok", pf["E"], ps["E"], rf, rs, (rr, bb, pr, pb))
