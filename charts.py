import glob
import json
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # draw straight to image files, no window
import matplotlib.pyplot as plt

RESULTS_FOLDER = "results/main"
ANALYSIS_FOLDER = "results/analysis"
FIGURE_FOLDER = "results/figures"

# Colors: one meaning each, the same in every chart
NEUTRAL = "#8a8985"       # all-neutral markets / no sale (the baseline)
UNDISCLOSED = "#2a78d6"   # blue: pro-A agents not told about each other / non-ally sells
DISCLOSED = "#eb6834"     # orange: pro-A agents told about each other / ally sells
MAIN = "#2a78d6"          # single-series charts
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_SECONDARY,
    "axes.titlecolor": TEXT,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
    "font.size": 10,
    "legend.frameon": False,
})

CONDITION_NAMES = {
    1: "1  Lone partisan (30%)", 2: "2  Lone partisan (10%)",
    3: "3  Undisclosed (30%)", 4: "4  Undisclosed (10%)",
    5: "5  Disclosed (30%)", 6: "6  Disclosed (10%)",
    7: "7  Undisclosed, wording 2", 8: "8  Disclosed, wording 2",
    9: "9  Undisclosed, wording 3", 10: "10  Disclosed, wording 3",
    14: "14  Phantom co-partisans", 17: "17  Told to coordinate",
}


def load_markets():
    markets = []
    for path in sorted(glob.glob(f"{RESULTS_FOLDER}/*.json")):
        with open(path) as f:
            markets.append(json.load(f))
    return markets


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{FIGURE_FOLDER}/{name}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Saved", f"{FIGURE_FOLDER}/{name}")


# ---------------------------------------------------------------
# Figure 1: sacrifice by condition, with 95% confidence intervals
# ---------------------------------------------------------------

def figure_sacrifice(by_condition):
    order = [1, 3, 5, 7, 8, 9, 10, 14, 17, 2, 4, 6]   # 30% conditions first, then 10%
    rows = by_condition.set_index("condition").loc[order]
    fig, ax = plt.subplots(figsize=(7, 5))
    y = list(range(len(order)))[::-1]
    ax.hlines(y, rows["S_ci_low"], rows["S_ci_high"], color=MAIN, linewidth=2)
    ax.plot(rows["S"], y, "o", color=MAIN, markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.axvline(0, color=TEXT_SECONDARY, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels([CONDITION_NAMES[c] for c in order])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Sacrifice S (% of $100 starting money), with 95% confidence interval")
    ax.set_title("Sacrifice by pro-A agents, by condition", loc="left")
    save(fig, "fig1_sacrifice_by_condition.png")


# ---------------------------------------------------------------
# Figure 2: the sacrifice comparisons, against zero and the 5% threshold
# ---------------------------------------------------------------

def figure_tests(tests):
    wanted = [
        ("C1 primary: collusion effect", "Told vs. not told (5 vs 3), primary"),
        ("Robustness: wording 2", "Told vs. not told, wording 2 (8 vs 7)"),
        ("Robustness: wording 3", "Told vs. not told, wording 3 (10 vs 9)"),
        ("C4 non-demand", "Real vs. phantom co-partisans (5 vs 14)"),
        ("Secondary: phantom vs lone", "Phantom vs. alone (14 vs 1)"),
        ("Check: positive control", "Told to coordinate vs. not told (17 vs 3)"),
    ]
    rows = tests.set_index("test").loc[[w[0] for w in wanted]]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    y = list(range(len(wanted)))[::-1]
    ax.hlines(y, rows["ci_low"], rows["ci_high"], color=MAIN, linewidth=2)
    ax.plot(rows["difference"], y, "o", color=MAIN, markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.axvline(0, color=TEXT_SECONDARY, linewidth=1)
    ax.axvline(5, color=TEXT_SECONDARY, linewidth=1, linestyle="--")
    ax.text(5, max(y) + 0.6, "C1 threshold (5) ", color=TEXT_SECONDARY, fontsize=9, va="bottom", ha="right")
    ax.set_xlim(right=max(5.5, rows["ci_high"].max() + 0.5))
    ax.set_yticks(y)
    ax.set_yticklabels([w[1] for w in wanted])
    ax.set_ylim(min(y) - 0.6, max(y) + 1.2)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Difference in sacrifice (percentage points), with 95% confidence interval")
    ax.set_title("Differences in sacrifice between conditions", loc="left")
    save(fig, "fig2_sacrifice_comparisons.png")


# ---------------------------------------------------------------
# Figure 3: average price of A by round
# ---------------------------------------------------------------

def average_price_path(markets, condition):
    paths = [m["price_history"] for m in markets if m["condition"] == condition]
    return [sum(p[r] for p in paths) / len(paths) for r in range(20)]


def figure_prices(markets):
    panels = [(0.30, [(15, "All neutral", NEUTRAL, ":"), (3, "Pro-A agents not told about each other", UNDISCLOSED, "-"), (5, "Pro-A agents told about each other", DISCLOSED, "--")]),
              (0.10, [(16, "All neutral", NEUTRAL, ":"), (4, "Pro-A agents not told about each other", UNDISCLOSED, "-"), (6, "Pro-A agents told about each other", DISCLOSED, "--")])]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    rounds = list(range(1, 21))
    for ax, (p_star, lines) in zip(axes, panels):
        ax.axhline(p_star, color=TEXT_SECONDARY, linewidth=1)
        ax.text(20.3, p_star, f"true chance\n{p_star:.0%}", color=TEXT_SECONDARY, fontsize=8, va="center")
        for condition, label, color, style in lines:
            ax.plot(rounds, average_price_path(markets, condition), color=color, linewidth=2,
                    linestyle=style, label=label)
        ax.set_title(f"A's true chance: {p_star:.0%}", loc="left")
        ax.set_xlabel("Round")
        ax.set_xlim(1, 20)
        ax.set_xticks([1, 5, 10, 15, 20])
    axes[0].set_ylabel("Average price of A")
    axes[0].set_ylim(0, 0.6)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, fontsize=9)
    fig.suptitle("Price of Candidate A over the market (three pro-A agents vs. all-neutral)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold", color=TEXT)
    save(fig, "fig3_price_paths.png")


# ---------------------------------------------------------------
# Figure 4: reliance test, net A bought by the pro-A agents each round
# ---------------------------------------------------------------

def average_net_A_by_round(markets, condition):
    totals = [0.0] * 20
    count = 0
    for m in markets:
        if m["condition"] != condition:
            continue
        count = count + 1
        pro_ids = [t["trader"] for t in m["traders"] if t["kind"] == "pro-A"]
        for r in m["records"]:
            if r["trader"] in pro_ids and r["executed"] and r["candidate"] == "A":
                if r["action"] == "buy":
                    totals[r["round"] - 1] += r["shares"]
                elif r["action"] == "sell":
                    totals[r["round"] - 1] -= r["shares"]
    return [t / count for t in totals]


def figure_reliance(markets):
    fig, ax = plt.subplots(figsize=(7, 3.8))
    rounds = list(range(1, 21))
    ax.axvspan(10.5, 15.5, color=GRID, alpha=0.6, linewidth=0)
    ax.text(13, 0.98, "bot sells A", transform=ax.get_xaxis_transform(), ha="center", va="top",
            color=TEXT_SECONDARY, fontsize=9)
    for condition, label, color, style in [(11, "No sale (11)", NEUTRAL, ":"),
                                           (12, "Co-partisan bot sells (12)", DISCLOSED, "--"),
                                           (13, "Non-partisan bot sells (13)", UNDISCLOSED, "-")]:
        ax.plot(rounds, average_net_A_by_round(markets, condition), color=color, linewidth=2,
                linestyle=style, label=label)
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=1)
    ax.set_xlim(1, 20)
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlabel("Round")
    ax.set_ylabel("Net A shares bought\nby the two pro-A agents")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=9)
    ax.set_title("A purchases by pro-A agents in the reliance conditions", loc="left")
    save(fig, "fig4_reliance.png")


os.makedirs(FIGURE_FOLDER, exist_ok=True)
markets = load_markets()
figure_sacrifice(pd.read_csv(f"{ANALYSIS_FOLDER}/sacrifice_and_distortion_by_condition.csv"))
figure_tests(pd.read_csv(f"{ANALYSIS_FOLDER}/tests_all_markets.csv"))
figure_prices(markets)
figure_reliance(markets)