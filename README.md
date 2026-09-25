# Knowing the Scale, Missing the Negation

Data and code for the paper **"Knowing the Scale, Missing the Negation: Language Models and Corrective Negation by Excess in English, Spanish, and French"** (Maikel Yelandi Leyva Vázquez, Universidad Bernardo O'Higgins / Universidad Bolivariana del Ecuador; Bastián Gutiérrez Vargas, Universidad Bernardo O'Higgins). Manuscript under review.

The study tests whether large language models understand *corrective negation by excess*, as in "it is not dim but dark", where "not" rejects the weaker adjective as too weak rather than denying it. For each adjective pair, a model is first tested on the scale ordering and on the affirmative entailment ("it is dark; is it at least dim?"). Its reading of corrective negation is then analysed only on the pairs where it passed those tests.

## Contents

| Path | Description |
|---|---|
| `data/pairs.json` | 450 sampled adjective pairs (weak X, strong Y, antonym where available), 150 per language (EN/ES/FR) |
| `data/items_p2.json` | Main items: ordering (A, Arev), plain negation (N), lexical corrective (E), same-word corrective (S), downward corrective (D) |
| `data/items_p2_v2.json` | Control items: affirmative entailment (P), reversed questions (N_b, E_b, S_b), *but rather* (EN) and *pero* (ES) |
| `data/excluded_pids.json` | 23 pairs excluded as ungrammatical or invalid (quantifiers, ordinals, antonym = X) |
| `data/screened_pids.json` | 180 further pairs set aside by the first author's screening, with the category of each |
| `results/raw/*.jsonl` | Raw model responses (OpenRouter, temperature 0), one JSON object per query |
| `results/analysis/results_p2_v4.txt` | Output of the analysis reported in the paper (full and screened sets) |
| `results/analysis/results_p2_v4_tiesfirst.txt` | Sensitivity analysis resolving tied repeated answers by the first answer |
| `code/` | Scripts to build items, query models, and analyse results |
| `get_scales.sh` | Downloads the source scale resources (not redistributed here) |

## Source scales

The adjective pairs were sampled from the DEMELO (de Melo & Bansal, 2013), CROWD (Cocos et al., 2018), and WILKINSON (Wilkinson & Oates, 2016) resources, in the English, Spanish, and French versions released by Garí Soler and Apidianaki (2020, 2021) at <https://github.com/ainagari/scalar_adjs>. That repository does not state a license, so its files are not redistributed here. `data/pairs.json` contains only the sampled adjective pairs derived from it. To rebuild the pairs from scratch, run `get_scales.sh` and then `code/build_items.py`.

## Reproducing the analysis

Requirements: Python 3.10+, `pandas`, `numpy`, `scipy`, `statsmodels`, `requests`.

```bash
cd code
cp ../data/*.json .
cp ../results/raw/*.jsonl .
python analyze_p2_v3.py          # main analysis (ties dropped)
python analyze_p2_v3.py first    # sensitivity: ties resolved by the first answer
```

To query models again, set the environment variable `OPENROUTER_API_KEY` and run `python run_p2.py fast items_p2.json`, `python run_p2.py strong items_p2.json`, and `python run_p2.py v2 items_p2_v2.json`. Model versions change over time, so new runs may not reproduce the raw responses exactly.

## Notes on the data

- Several prompts are shared by different pairs, and some prompts were queried more than once. The analysis uses the majority answer per model and prompt and drops ties (5.9% of repeated prompts received inconsistent answers at temperature 0).
- Llama 3.1 8B responses are included in the raw files but excluded from the analysis (see the paper). Mistral Small was dropped because of rate limits.
- The Spanish *pero* condition is included for completeness. Because *pero* after a negation is standardly concessive, it is not a valid test of corrective reading and is reported only descriptively.

## License

Code: MIT License. Data produced in this study (items, raw responses, screening lists, analysis outputs): CC BY 4.0. See `LICENSE`.

## Citation

Leyva Vázquez, M. Y., & Gutiérrez Vargas, B. (2026). *Knowing the scale, missing the negation: Language models and corrective negation by excess in English, Spanish, and French* [Manuscript submitted for publication].

## References

- Cocos, A., Wharton, S., Pavlick, E., Apidianaki, M., & Callison-Burch, C. (2018). Learning scalar adjective intensity from paraphrases. *EMNLP 2018*, 1752–1762.
- de Melo, G., & Bansal, M. (2013). Good, great, excellent: Global inference of semantic intensities. *TACL*, 1, 279–290.
- Garí Soler, A., & Apidianaki, M. (2020). BERT knows Punta Cana is not just beautiful, it's gorgeous. *EMNLP 2020*, 7371–7385.
- Garí Soler, A., & Apidianaki, M. (2021). Scalar adjective identification and multilingual ranking. *NAACL 2021*, 4653–4660.
- Wilkinson, B., & Oates, T. (2016). A gold standard for scalar adjectives. *LREC 2016*, 2669–2675.
