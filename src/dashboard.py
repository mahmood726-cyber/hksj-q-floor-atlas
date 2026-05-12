"""Offline-only dashboard: matplotlib PNGs + Jinja2 HTML."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).parent / "templates"
HIST_BINS = np.logspace(0.0, 1.0, 21)  # 20 bins, ratio 1.0x to 10.0x on log-x


def _render_histogram(per_ma: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(per_ma["ci_width_ratio"].values, bins=HIST_BINS, color="#555",
            edgecolor="#222")
    ax.set_xscale("log")
    ax.set_xlabel("CI-width ratio (floored / un-floored)")
    ax.set_ylabel("count")
    ax.set_title("HKSJ Q-floor CI-width inflation (I^2=0 subset)")
    ax.axvline(1.0, color="red", linestyle="--", linewidth=1)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def _render_forest(row: pd.Series, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 1.8))
    est = row["estimate"]
    ax.errorbar([est], [1], xerr=[[est - row["ci_lo_unfloored"]],
                                   [row["ci_hi_unfloored"] - est]],
                fmt="o", color="black", capsize=5, label="HKSJ no-floor")
    ax.errorbar([est], [0], xerr=[[est - row["ci_lo_floored"]],
                                   [row["ci_hi_floored"] - est]],
                fmt="s", color="#c44", capsize=5, label="HKSJ + Q-floor")
    ax.axvline(0, color="grey", linewidth=0.7)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["floored", "un-floored"])
    ax.set_xlabel("effect (log-scale or SMD)")
    ax.set_title(f"{row['ma_id']}  (k={int(row['k'])})")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def _select_examples(per_ma: pd.DataFrame) -> pd.DataFrame:
    """Pick 3 worked examples: highest CI-ratio in k=2, median k=3-5, sig-loss case."""
    examples = []
    k2 = per_ma[per_ma["k"] == 2]
    if not k2.empty:
        examples.append(k2.loc[k2["ci_width_ratio"].idxmax()])
    midk = per_ma[per_ma["k"].between(3, 5)]
    if not midk.empty:
        sorted_mid = midk.sort_values("ci_width_ratio")
        examples.append(sorted_mid.iloc[len(sorted_mid) // 2])
    sig_losses = per_ma[per_ma["sig_loss"]]
    if not sig_losses.empty:
        examples.append(sig_losses.iloc[0])
    while len(examples) < 3:
        examples.append(per_ma.iloc[len(examples)])
    return pd.DataFrame(examples[:3])


def render_dashboard(atlas: pd.DataFrame, per_ma: pd.DataFrame,
                     out_dir: Path) -> None:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    _render_histogram(per_ma, assets / "ratio_histogram.png")
    examples_df = _select_examples(per_ma)
    for i, (_, row) in enumerate(examples_df.iterrows()):
        _render_forest(row, assets / f"forest_{i}.png")

    overall = atlas[atlas["stratum"] == "overall"].iloc[0]
    strata = atlas[atlas["stratum"] != "overall"]

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)),
                      autoescape=True, keep_trailing_newline=False)
    tmpl = env.get_template("index.html.j2")
    html = tmpl.render(
        overall=overall.to_dict(),
        strata=strata.to_dict(orient="records"),
        examples=examples_df.to_dict(orient="records"),
        generated_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8", newline="\n")
