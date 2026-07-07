# Claud-Minions

A team of Claude Code agents and skills for **environmental toxicology research** — focused on how environmental factors (endocrine-disrupting chemicals, dietary/food-safety exposures) drive **metabolic and reproductive disease** risk.

Built as a Claude Code plugin: specialized subagents ("minions") delegate to reusable skills that carry the domain know-how and runnable Python scripts.

## What's inside

### Agents (`agents/`)
| Agent | Role |
|-------|------|
| **lit-scout** | Systematic literature search + abstract screening → evidence tables & PRISMA-style log |
| **tox-profiler** | Chemical identity + tox/mechanistic profile from PubChem & EPA CompTox |
| **bioassay-analyst** | Plate QC, normalization, and dose-response fitting for reporter-gene / high-content assays |
| **aop-mapper** | Adverse Outcome Pathways linking a chemical → mechanism → metabolic/reproductive endpoint |
| **sci-writer** | Journal-style Methods/Results/Discussion drafting with no fabricated claims |

### Skills (`skills/`)
| Skill | What it packages |
|-------|------------------|
| **dose-response-fitting** | 4-parameter logistic fit → EC50/IC50 + 95% CI, Hill slope, R² (Python) |
| **assay-qc** | Z'-factor, control CV, outlier flags, normalization (Python) |
| **pubmed-search** | Reproducible Europe PMC / NCBI queries + screening log (Python, no API key) |
| **chem-lookup** | PubChem identity/properties + optional EPA CompTox/ToxCast bioactivity (Python) |
| **aop-diagram** | Render an AOP node/edge list to a Mermaid flowchart + PNG (Python) |
| **exposure-context** | Margin of exposure: in vitro EC50 vs realistic human exposure, with unit conversion (Python) |
| **pub-figures** | Publication-ready matplotlib style + colorblind-safe palette (Python) |

### Commands (`commands/`)
- `/litreview <topic>` — run lit-scout end to end
- `/edc-mdc-daily-update [scope]` — collect the newest EDC/MDC studies and nutrient-protection evidence in a daily table
- `/profile-chemical <name|CAS>` — run tox-profiler
- `/analyze-assay <data.csv>` — run bioassay-analyst

### Try it (`examples/`)
A runnable, end-to-end walkthrough on simulated assay data — QC → dose-response fit →
human-relevance context. See [examples/README.md](examples/README.md).

## Design principles
- **Reproducible**: searches save their exact query; analyses save parameters, scripts, and data.
- **No fabrication**: every citation, CAS, and statistic traces to a real retrieved source.
- **Evidence honesty**: in vitro / animal / human claims kept distinct; predicted values marked; EC50s never reported without CI + R².

## Setup

Install the Python dependencies used by the skills:

```bash
pip install numpy scipy pandas matplotlib requests
```

Install as a Claude Code plugin (from a marketplace or local path), then invoke a minion:

```
/analyze-assay data/plate1.csv
> use the bioassay-analyst agent to fit the dose-response for compound X
```

## Repository layout
```
.claude-plugin/plugin.json   # plugin manifest
agents/                      # 5 subagent definitions
skills/                      # 5 skills, each SKILL.md + scripts/
commands/                    # slash-command entry points
```

## Author
Yuling Xie — Institute for Global Food Security, Queen's University Belfast.
<https://cher-dou.github.io>
