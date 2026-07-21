# Claud-Minions

A team of Claude Code agents and skills for **environmental toxicology research** — focused on how environmental factors (endocrine-disrupting chemicals, dietary/food-safety exposures) drive **metabolic and reproductive disease** risk.

Built as a Claude Code plugin: specialized subagents ("minions") delegate to reusable skills that carry the domain know-how and runnable Python scripts.

## What's inside

### Agents (`agents/`)
| Agent | Role |
|-------|------|
| **research-manager** | Orchestrates broad research questions across specialist agents, evidence ledgers, and quality gates |
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
- `/research <question>` — route a broad question through the research-manager and specialist agents
- `/litreview <topic>` — run lit-scout end to end
- `/edc-mdc-daily-update [scope]` — collect the newest EDC/MDC studies and nutrient-protection evidence in a daily table
- `/profile-chemical <name|CAS>` — run tox-profiler
- `/analyze-assay <data.csv>` — run bioassay-analyst

### Agent architecture
`research-manager` coordinates the platform: it frames the research question,
routes work to the right specialist agents and skills, keeps an evidence ledger,
and applies quality gates before synthesis. See
[docs/agent-architecture.md](docs/agent-architecture.md) for the workflow,
quality gates, and roadmap toward memory, evidence scoring, and a knowledge graph.

### Benchmark roadmap
The first evaluation benchmark is intentionally small. The broader plan is
AIToxBench: a versioned benchmark suite for EDC/MDC literature screening,
nutrient-protection evidence, fertility, metabolism, gut mechanisms, chemical
profiling, assay analysis, AOP mapping, and scientific writing. See
[benchmarks/AIToxBench/](benchmarks/AIToxBench/).

### Cloud automation
A scheduled GitHub Actions runner can create the daily EDC/MDC Google Doc and update the Evidence Tracker before any local device is open. See [docs/cloud-runner-setup.md](docs/cloud-runner-setup.md).

### Evaluation (`evals/`)
`lit-scout` is evaluated against a scientist-reviewed benchmark containing
relevant, irrelevant, and borderline environmental-toxicology papers.

| Metric | Result |
|---|---:|
| Screening precision | TBD |
| Screening recall | TBD |
| Citation validity | TBD |
| Evidence-field accuracy | TBD |
| Unsupported claims | TBD |

See [`evals/lit_scout/`](evals/lit_scout/) for the gold-standard dataset,
prediction template, evaluation script, and reproducibility instructions.

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

For the cloud daily EDC/MDC report, install the cloud dependencies in GitHub Actions with:

```bash
pip install -r requirements-cloud.txt
```

## Repository layout
```
.claude-plugin/plugin.json   # plugin manifest
agents/                      # orchestration and specialist agent definitions
docs/                        # cloud setup and architecture notes
skills/                      # reusable skills, each SKILL.md + scripts/
commands/                    # slash-command entry points
evals/                       # gold-standard benchmarks and evaluation scripts
benchmarks/                  # long-term benchmark roadmap and datasets
```

## Author
Yuling Xie — Institute for Global Food Security, Queen's University Belfast.
<https://cher-dou.github.io>
