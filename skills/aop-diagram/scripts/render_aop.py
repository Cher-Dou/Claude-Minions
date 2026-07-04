#!/usr/bin/env python3
"""Render an Adverse Outcome Pathway (node/edge JSON) to Mermaid + PNG.

Usage:
    python render_aop.py aop.json --out results/aop

Outputs <out>.mmd, <out>.md (fenced mermaid), and <out>.png (if matplotlib present).
"""
import argparse
import json
import os
import sys

# Mermaid line styles by confidence
MERMAID_EDGE = {"strong": "-->", "moderate": "-.->", "weak": "-..->"}
MPL_LINESTYLE = {"strong": "-", "moderate": "--", "weak": ":"}
NODE_COLOR = {"mie": "#0072B2", "ke": "#56B4E9", "ao": "#D55E00"}


def load(path):
    with open(path) as f:
        aop = json.load(f)
    for key in ("mie", "ao", "kers"):
        if key not in aop:
            sys.exit(f"Input missing required key: '{key}'")
    aop.setdefault("key_events", [])
    aop.setdefault("title", "Adverse Outcome Pathway")
    return aop


def sanitize(label):
    return label.replace('"', "'").replace("\n", " ")


def to_mermaid(aop):
    lines = ["flowchart TD"]
    lines.append(f'    {aop["mie"]["id"]}["MIE: {sanitize(aop["mie"]["label"])}"]')
    for ke in aop["key_events"]:
        lvl = f' ({ke["level"]})' if ke.get("level") else ""
        lines.append(f'    {ke["id"]}["KE: {sanitize(ke["label"])}{lvl}"]')
    lines.append(f'    {aop["ao"]["id"]}["AO: {sanitize(aop["ao"]["label"])}"]')
    lines.append("")
    for ker in aop["kers"]:
        arrow = MERMAID_EDGE.get(ker.get("confidence", "moderate"), "-.->")
        ev = ker.get("evidence", "")
        edge = f'    {ker["from"]} {arrow}'
        if ev:
            edge += f'|{sanitize(ev)}|'
        edge += f' {ker["to"]}'
        lines.append(edge)
    lines.append("")
    lines.append(f'    style {aop["mie"]["id"]} fill:{NODE_COLOR["mie"]},color:#fff')
    lines.append(f'    style {aop["ao"]["id"]} fill:{NODE_COLOR["ao"]},color:#fff')
    return "\n".join(lines)


def to_png(aop, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    except ImportError:
        return None

    # Ordered node stack: MIE -> KEs -> AO
    nodes = [("mie", aop["mie"])]
    nodes += [("ke", ke) for ke in aop["key_events"]]
    nodes += [("ao", aop["ao"])]
    n = len(nodes)

    fig, ax = plt.subplots(figsize=(5, 0.9 * n + 1), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, n + 1)
    ax.axis("off")
    ax.set_title(sanitize(aop["title"]), fontsize=10, pad=10)

    pos = {}
    for i, (kind, node) in enumerate(nodes):
        y = n - i
        pos[node["id"]] = y
        prefix = {"mie": "MIE", "ke": "KE", "ao": "AO"}[kind]
        lvl = f'\n({node["level"]})' if node.get("level") else ""
        box = FancyBboxPatch((2, y - 0.32), 6, 0.64,
                             boxstyle="round,pad=0.02,rounding_size=0.12",
                             linewidth=1, edgecolor="#333",
                             facecolor=NODE_COLOR[kind],
                             alpha=0.9 if kind != "ke" else 0.75)
        ax.add_patch(box)
        txt_color = "white" if kind in ("mie", "ao") else "black"
        ax.text(5, y, f'{prefix}: {sanitize(node["label"])}{lvl}',
                ha="center", va="center", fontsize=7.5, color=txt_color, wrap=True)

    for ker in aop["kers"]:
        if ker["from"] not in pos or ker["to"] not in pos:
            continue
        y0, y1 = pos[ker["from"]], pos[ker["to"]]
        ls = MPL_LINESTYLE.get(ker.get("confidence", "moderate"), "--")
        arrow = FancyArrowPatch((5, y0 - 0.33), (5, y1 + 0.33),
                                arrowstyle="-|>", mutation_scale=12,
                                linewidth=1.2, linestyle=ls, color="#444")
        ax.add_patch(arrow)
        if ker.get("evidence"):
            ax.text(8.2, (y0 + y1) / 2, sanitize(ker["evidence"]),
                    ha="left", va="center", fontsize=6, color="#666", style="italic")

    fig.tight_layout()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    ap = argparse.ArgumentParser(description="Render an AOP to Mermaid + PNG.")
    ap.add_argument("json")
    ap.add_argument("--out", default="aop")
    args = ap.parse_args()

    aop = load(args.json)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    mermaid = to_mermaid(aop)
    mmd_path = f"{args.out}.mmd"
    md_path = f"{args.out}.md"
    with open(mmd_path, "w") as f:
        f.write(mermaid + "\n")
    with open(md_path, "w") as f:
        f.write(f"# {aop['title']}\n\n```mermaid\n{mermaid}\n```\n")

    print(f"Saved Mermaid source -> {mmd_path}")
    print(f"Saved Markdown       -> {md_path}")

    png = to_png(aop, f"{args.out}.png")
    if png:
        print(f"Saved PNG            -> {png}")
    else:
        print("PNG skipped (matplotlib not installed).")


if __name__ == "__main__":
    main()
