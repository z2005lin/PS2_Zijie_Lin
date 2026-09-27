import json
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
OUTPUT = repo_root / "notebooks" / "Algorand_PS2_Fee_Choice_Game.ipynb"

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip() + "\n"}

def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip() + "\n",
    }

cells = [
md(r"""
# Strategic Fee-Level Choice under Incomplete Information

This notebook studies a one-shot static Bayesian anti-coordination game for two Algorand users. Each user privately observes whether the transaction is **urgent** or **patient**, then simultaneously chooses **High Fee** or **Low Fee**.

- If both users choose the same fee level, congestion occurs and both receive the low congestion reward.
- If choices differ, the High Fee user receives the high reward and the Low Fee user receives the differentiated low-fee reward.

The main comparison is:

| Treatment | Information available before choice | Research purpose |
|---|---|---|
| Complete information | Both transaction types are known | Coordination benchmark |
| Incomplete information | Each user knows only their own type and the common prior | Bayesian baseline |
| Incomplete information + signal | Baseline information plus a coordination recommendation | Information-design treatment |

This notebook is a **planned computational experiment**. Payoffs, type probabilities, and signal accuracy are transparent experimental inputs, not measured Algorand protocol facts. All generated values are simulated rather than empirical results.
"""),
md(r"""
## 1. Game

**Players.** Two transaction users, $i\in\{1,2\}$.

**Private type**

$$
\theta_i \in \{\text{urgent},\text{patient}\}.
$$

**Action**

$$
a_i \in \{H,L\},
$$

where $H$ is High Fee and $L$ is Low Fee.

**Information.** Each user observes their own type. The treatment determines whether the other type or a coordination signal is also observed.

**Payoffs.** If actions match, both receive $R_C(\theta_i)$. If actions differ, the High Fee user receives $R_H(\theta_i)$ and the Low Fee user receives $R_L(\theta_i)$. The benchmark assumes

$$
R_H(\theta)>R_L(\theta)>R_C(\theta).
$$

**Solution concepts.** Complete-information Nash equilibrium and incomplete-information Bayesian Nash equilibrium. A welfare benchmark assigns one user to each fee level and gives High Fee to the more urgent type when types differ.
"""),
code(r"""
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from copy import deepcopy

SEED = 206
"""),
md(r"""
## 2. Reduced two-user matrix game

The proposal's strategic model is a single simultaneous-move stage game. Nature first draws private types. Users then choose High Fee or Low Fee without observing the other user's action.

The symbolic payoff matrix is:

| User 1 / User 2 | High Fee | Low Fee |
|---|---:|---:|
| **High Fee** | $(R_C,R_C)$ | $(R_H,R_L)$ |
| **Low Fee** | $(R_L,R_H)$ | $(R_C,R_C)$ |

Under $R_H>R_L>R_C$, the complete-information benchmark has two asymmetric pure equilibria, $(H,L)$ and $(L,H)$. The figure below makes the congestion and differentiation regions explicit.
"""),
code(r"""
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(9, 5.2))
ax.set_xlim(0, 3.2)
ax.set_ylim(0, 3.0)
ax.axis("off")

ax.text(1.9, 2.82, "User 2", ha="center", fontsize=12, fontweight="bold")
ax.text(0.18, 1.45, "User 1", ha="center", rotation=90,
        fontsize=12, fontweight="bold")

ax.text(1.35, 2.48, "High Fee", ha="center", fontweight="bold")
ax.text(2.45, 2.48, "Low Fee", ha="center", fontweight="bold")
ax.text(0.70, 1.95, "High Fee", ha="center", fontweight="bold")
ax.text(0.70, 0.85, "Low Fee", ha="center", fontweight="bold")

cells_to_draw = [
    (0.95, 1.45, 0.80, 0.80, "$(R_C,R_C)$\nCongestion", "#fde8e5", "#e64b35"),
    (2.05, 1.45, 0.80, 0.80, "$(R_H,R_L)$\nDifferentiated", "#e3f4f1", "#14877d"),
    (0.95, 0.35, 0.80, 0.80, "$(R_L,R_H)$\nDifferentiated", "#e3f4f1", "#14877d"),
    (2.05, 0.35, 0.80, 0.80, "$(R_C,R_C)$\nCongestion", "#fde8e5", "#e64b35"),
]

for x, y, w, h, label, face, edge in cells_to_draw:
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.05",
        facecolor=face, edgecolor=edge, linewidth=1.8
    ))
    ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=11)

ax.text(1.9, 0.08, "$R_H > R_L > R_C$: differentiation is preferred to congestion",
        ha="center", fontsize=10)
ax.set_title("One-shot fee-choice anti-coordination game", fontsize=15, fontweight="bold")
plt.show()
"""),
md(r"""
The one-shot causal chain is:

$$
(\theta_1,\theta_2)
\rightarrow
\text{information treatment}
\rightarrow
(a_1,a_2)
\rightarrow
\text{congestion, sorting, and welfare}.
$$

Unlike the earlier dynamic notebook, there is no Submit/Wait continuation state. Repeated rounds are independent random matches used to estimate choice frequencies and learning; they do not change the stage game into a dynamic game.
"""),
md(r"""
## 3. Simulation parameters

The two types differ in the relative value of obtaining High Fee priority. The calibration below satisfies $R_H>R_L>R_C$ for both types and makes urgent users more strongly prefer High Fee.

The prior probability of an urgent type, payoff magnitudes, tremble rate, and signal accuracy are experimental assumptions. They must be replaced by preregistered values before a real study.
"""),
code(r"""
@dataclass
class Params:
    pairs_per_seed: int = 5_000
    seeds: int = 20
    urgent_prob: float = 0.60
    tremble: float = 0.03
    signal_accuracy: float = 0.85

P = Params()

PAYOFF = {
    "urgent":  {"R_H": 8.0, "R_L": 2.0, "R_C": 1.0},
    "patient": {"R_H": 5.0, "R_L": 4.0, "R_C": 1.0},
}

def draw_types(rng, p=P):
    return tuple(
        "urgent" if rng.random() < p.urgent_prob else "patient"
        for _ in range(2)
    )

def payoff(typ, own_action, other_action):
    q = PAYOFF[typ]
    if own_action == other_action:
        return q["R_C"]
    return q["R_H"] if own_action == "H" else q["R_L"]

def efficient_assignment(types, rng):
    if types[0] != types[1]:
        return ("H", "L") if types[0] == "urgent" else ("L", "H")
    return ("H", "L") if rng.random() < 0.5 else ("L", "H")
"""),
md(r"""
## 4. Bayesian best response

Let $q$ be the probability that the other user chooses High Fee. For type $\theta$,

$$
EU(H\mid\theta,q)=qR_C(\theta)+(1-q)R_H(\theta),
$$

$$
EU(L\mid\theta,q)=qR_L(\theta)+(1-q)R_C(\theta).
$$

The type is indifferent when

$$
q^*(\theta)=
\frac{R_H(\theta)-R_C(\theta)}
{R_H(\theta)+R_L(\theta)-2R_C(\theta)}.
$$

A pure Bayesian strategy maps each private type to $H$ or $L$. It is an equilibrium only if the marginal action probability induced by the type prior makes every type's assigned action a best response.
"""),
code(r"""
def high_threshold(typ):
    q = PAYOFF[typ]
    return (q["R_H"] - q["R_C"]) / (
        q["R_H"] + q["R_L"] - 2 * q["R_C"]
    )

def expected_payoffs(typ, prob_other_high):
    q = PAYOFF[typ]
    eu_h = prob_other_high * q["R_C"] + (1-prob_other_high) * q["R_H"]
    eu_l = prob_other_high * q["R_L"] + (1-prob_other_high) * q["R_C"]
    return eu_h, eu_l

def best_response(typ, prob_other_high, atol=1e-10):
    eu_h, eu_l = expected_payoffs(typ, prob_other_high)
    if np.isclose(eu_h, eu_l, atol=atol):
        return "Mix"
    return "H" if eu_h > eu_l else "L"

def pure_bayesian_equilibria(urgent_prob):
    equilibria = []
    for urgent_action, patient_action in itertools.product(["H", "L"], repeat=2):
        strategy = {"urgent": urgent_action, "patient": patient_action}
        q_high = (
            urgent_prob * (urgent_action == "H")
            + (1-urgent_prob) * (patient_action == "H")
        )
        stable = all(
            best_response(typ, q_high) in {action, "Mix"}
            for typ, action in strategy.items()
        )
        if stable:
            equilibria.append({
                "urgent_action": urgent_action,
                "patient_action": patient_action,
                "marginal_prob_high": q_high,
            })
    return pd.DataFrame(equilibria)

display(pd.DataFrame({
    "type": list(PAYOFF),
    "high_indifference_threshold": [high_threshold(t) for t in PAYOFF],
}).round(3))

display(pure_bayesian_equilibria(P.urgent_prob))
"""),
md(r"""
### Decision diagnostic

Before simulating treatments, verify that the proposed type strategy is a Bayesian best response under the chosen prior. A useful calibration contains a region in which urgent users choose High Fee and patient users choose Low Fee; otherwise the intended type-sorting mechanism is inactive.

The diagnostic below enumerates all pure type-contingent Bayesian equilibria over a range of urgent-type probabilities.
"""),
code(r"""
diagnostic_rows = []

for urgent_prob in np.round(np.linspace(0.05, 0.95, 19), 2):
    eq = pure_bayesian_equilibria(urgent_prob)
    if len(eq) == 0:
        diagnostic_rows.append({
            "urgent_prob": urgent_prob,
            "equilibrium": "no pure BNE",
            "marginal_prob_high": np.nan,
        })
    else:
        for _, row in eq.iterrows():
            diagnostic_rows.append({
                "urgent_prob": urgent_prob,
                "equilibrium": f"U->{row['urgent_action']}, P->{row['patient_action']}",
                "marginal_prob_high": row["marginal_prob_high"],
            })

decision_diagnostic = pd.DataFrame(diagnostic_rows)
display(decision_diagnostic)
"""),
md(r"""
## 5. Many-pair static simulation

Each observation is an independent two-user match:

1. Nature draws two private types.
2. The treatment determines available information.
3. Users simultaneously choose High Fee or Low Fee.
4. The program records congestion, successful differentiation, whether the urgent type receives High Fee, individual payoffs, and total welfare.

The complete-information treatment implements the efficient differentiated benchmark. The incomplete-information treatment uses a type-contingent Bayesian strategy. In the signal treatment, the mechanism recommends the efficient differentiated assignment; each user follows the recommendation with the specified probability and otherwise falls back to the Bayesian action.
"""),
code(r"""
def bayesian_action(typ):
    # Calibrated pure BNE at the baseline prior; checked in the diagnostic above.
    return "H" if typ == "urgent" else "L"

def maybe_tremble(action, rng, tremble):
    if rng.random() < tremble:
        return "L" if action == "H" else "H"
    return action

def choose_actions(types, treatment, rng, p=P):
    if treatment == "complete_information":
        intended = efficient_assignment(types, rng)
    elif treatment == "incomplete_information":
        intended = tuple(bayesian_action(t) for t in types)
    elif treatment == "signal":
        recommendation = efficient_assignment(types, rng)
        intended = tuple(
            recommendation[i]
            if rng.random() < p.signal_accuracy
            else bayesian_action(types[i])
            for i in range(2)
        )
    else:
        raise ValueError(f"Unknown treatment: {treatment}")

    return tuple(maybe_tremble(a, rng, p.tremble) for a in intended)

def run_experiment(seed=0, treatment="incomplete_information", p=P):
    rng = np.random.default_rng(seed)
    rows = []

    for pair_id in range(p.pairs_per_seed):
        types = draw_types(rng, p)
        actions = choose_actions(types, treatment, rng, p)
        payoffs = (
            payoff(types[0], actions[0], actions[1]),
            payoff(types[1], actions[1], actions[0]),
        )

        differentiated = actions[0] != actions[1]
        mixed_types = types[0] != types[1]
        urgent_high = (
            (types[0] == "urgent" and actions[0] == "H")
            or (types[1] == "urgent" and actions[1] == "H")
        ) if mixed_types else np.nan

        rows.append({
            "seed": seed,
            "pair_id": pair_id,
            "treatment": treatment,
            "type_1": types[0],
            "type_2": types[1],
            "action_1": actions[0],
            "action_2": actions[1],
            "same_fee_congestion": int(not differentiated),
            "differentiated": int(differentiated),
            "mixed_types": int(mixed_types),
            "urgent_high": urgent_high,
            "payoff_1": payoffs[0],
            "payoff_2": payoffs[1],
            "total_welfare": sum(payoffs),
        })

    return pd.DataFrame(rows)

def summarize(df):
    mixed = df[df["mixed_types"] == 1]
    return {
        "same_fee_congestion": df["same_fee_congestion"].mean(),
        "successful_differentiation": df["differentiated"].mean(),
        "efficient_type_sorting": mixed["urgent_high"].mean(),
        "mean_total_welfare": df["total_welfare"].mean(),
        "high_fee_share": (
            (df["action_1"] == "H").sum() + (df["action_2"] == "H").sum()
        ) / (2 * len(df)),
    }
"""),
md(r"""
## 6. Main three-treatment comparison

The three conditions isolate the value of information and coordination:

- **Complete information:** an upper benchmark for type-aware differentiation.
- **Incomplete information:** the static Bayesian baseline.
- **Incomplete information + signal:** an information-design treatment using a nonbinding recommendation.

The simulation reports means across independent random seeds. These are model-generated predictions under the stated calibration, not empirical findings.
"""),
code(r"""
summary_rows = []
raw_runs = []

for treatment in ["complete_information", "incomplete_information", "signal"]:
    for seed in range(P.seeds):
        data = run_experiment(seed=seed, treatment=treatment, p=P)
        raw_runs.append(data)
        row = summarize(data)
        row.update({"treatment": treatment, "seed": seed})
        summary_rows.append(row)

results = pd.DataFrame(summary_rows)
experiment_data = pd.concat(raw_runs, ignore_index=True)

summary = results.groupby("treatment").agg(
    same_fee_congestion=("same_fee_congestion", "mean"),
    successful_differentiation=("successful_differentiation", "mean"),
    efficient_type_sorting=("efficient_type_sorting", "mean"),
    mean_total_welfare=("mean_total_welfare", "mean"),
    high_fee_share=("high_fee_share", "mean"),
).reset_index()

display(summary.round(3))
"""),
code(r"""
metrics = [
    ("same_fee_congestion", "Same-fee congestion"),
    ("efficient_type_sorting", "Efficient type sorting"),
    ("mean_total_welfare", "Mean total welfare"),
]

fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))

for ax, (metric, title) in zip(axes, metrics):
    ax.bar(summary["treatment"], summary[metric], color=["#315efb", "#e64b35", "#14877d"])
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)

fig.suptitle("Planned treatment comparison under the baseline calibration", fontweight="bold")
fig.tight_layout()
plt.show()
"""),
md(r"""
## 7. Sensitivity to the type prior and signal accuracy

Bayesian behavior depends on beliefs about the other user's type. Signal performance also depends on whether users follow the recommendation.

This sensitivity analysis varies:

- the prior probability of an urgent user; and
- the probability that a user follows the coordination signal.

For each parameter pair, the analysis records same-fee congestion and welfare in the signal treatment.
"""),
code(r"""
def sensitivity_run(urgent_probs, signal_accuracies, seeds=range(10)):
    rows = []

    for urgent_prob in urgent_probs:
        for signal_accuracy in signal_accuracies:
            p = deepcopy(P)
            p.urgent_prob = urgent_prob
            p.signal_accuracy = signal_accuracy

            for seed in seeds:
                data = run_experiment(seed=seed, treatment="signal", p=p)
                row = summarize(data)
                row.update({
                    "urgent_prob": urgent_prob,
                    "signal_accuracy": signal_accuracy,
                    "seed": seed,
                })
                rows.append(row)

    return pd.DataFrame(rows)

sensitivity = sensitivity_run(
    urgent_probs=[0.2, 0.4, 0.6, 0.8],
    signal_accuracies=[0.5, 0.65, 0.8, 0.95, 1.0],
)

sensitivity_summary = sensitivity.groupby(
    ["urgent_prob", "signal_accuracy"]
).agg(
    same_fee_congestion=("same_fee_congestion", "mean"),
    efficient_type_sorting=("efficient_type_sorting", "mean"),
    mean_total_welfare=("mean_total_welfare", "mean"),
).reset_index()

display(sensitivity_summary.round(3))
"""),
code(r"""
pivot = sensitivity_summary.pivot(
    index="urgent_prob",
    columns="signal_accuracy",
    values="same_fee_congestion",
)

fig, ax = plt.subplots(figsize=(7.5, 4.2))
im = ax.imshow(pivot.values, aspect="auto", cmap="Reds", vmin=0, vmax=1)

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_xlabel("Signal-following probability")
ax.set_ylabel("Prior probability of urgent type")
ax.set_title("Same-fee congestion in the signal treatment")

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        ax.text(j, i, f"{pivot.iloc[i, j]:.2f}", ha="center", va="center")

plt.colorbar(im, ax=ax, label="Same-fee congestion rate")
plt.show()
"""),
md(r"""
## 8. Bayesian strategy versus simple behavioral benchmarks

This comparison asks whether type-contingent Bayesian choice improves coordination relative to simple alternatives:

- **Bayesian type strategy:** urgent chooses High Fee; patient chooses Low Fee under the baseline calibration.
- **Random choice:** each user independently chooses High Fee with probability one half.
- **Always High:** every user chooses High Fee.

The comparison is not evidence about real users. It shows which aggregate patterns are generated mechanically by alternative decision rules.
"""),
code(r"""
def run_behavior(seed, behavior, p=P):
    rng = np.random.default_rng(seed)
    rows = []

    for pair_id in range(p.pairs_per_seed):
        types = draw_types(rng, p)

        if behavior == "bayesian":
            actions = tuple(bayesian_action(t) for t in types)
        elif behavior == "random":
            actions = tuple("H" if rng.random() < 0.5 else "L" for _ in range(2))
        elif behavior == "always_high":
            actions = ("H", "H")
        else:
            raise ValueError(behavior)

        payoffs = (
            payoff(types[0], actions[0], actions[1]),
            payoff(types[1], actions[1], actions[0]),
        )
        mixed = types[0] != types[1]
        rows.append({
            "behavior": behavior,
            "same_fee_congestion": int(actions[0] == actions[1]),
            "efficient_type_sorting": (
                ((types[0] == "urgent" and actions[0] == "H")
                 or (types[1] == "urgent" and actions[1] == "H"))
                if mixed else np.nan
            ),
            "total_welfare": sum(payoffs),
        })

    return pd.DataFrame(rows)

behavior_rows = []
for behavior in ["bayesian", "random", "always_high"]:
    for seed in range(P.seeds):
        d = run_behavior(seed, behavior, P)
        behavior_rows.append({
            "behavior": behavior,
            "seed": seed,
            "same_fee_congestion": d["same_fee_congestion"].mean(),
            "efficient_type_sorting": d["efficient_type_sorting"].mean(),
            "mean_total_welfare": d["total_welfare"].mean(),
        })

behavior_comparison = pd.DataFrame(behavior_rows)
display(behavior_comparison.groupby("behavior").mean(numeric_only=True).round(3))
"""),
md(r"""
## 9. Welfare-maximizing assignment benchmark

For each pair, a planner must assign exactly one user to High Fee and one to Low Fee. The planner compares the welfare from $(H,L)$ and $(L,H)$:

$$
W(H,L)=R_H(\theta_1)+R_L(\theta_2),
$$

$$
W(L,H)=R_L(\theta_1)+R_H(\theta_2).
$$

The larger value defines the efficient assignment. Comparing treatment welfare with this capacity-matched benchmark identifies the welfare loss from congestion or incorrect type sorting.
"""),
code(r"""
def planner_welfare(types):
    w_hl = PAYOFF[types[0]]["R_H"] + PAYOFF[types[1]]["R_L"]
    w_lh = PAYOFF[types[0]]["R_L"] + PAYOFF[types[1]]["R_H"]
    return max(w_hl, w_lh)

planner_rows = []

for treatment in ["complete_information", "incomplete_information", "signal"]:
    for seed in range(P.seeds):
        data = run_experiment(seed=seed, treatment=treatment, p=P)
        data = data.copy()
        data["planner_welfare"] = [
            planner_welfare((t1, t2))
            for t1, t2 in zip(data["type_1"], data["type_2"])
        ]
        planner_rows.append({
            "treatment": treatment,
            "seed": seed,
            "realized_welfare": data["total_welfare"].mean(),
            "planner_welfare": data["planner_welfare"].mean(),
            "welfare_gap": (data["planner_welfare"] - data["total_welfare"]).mean(),
        })

planner_comparison = pd.DataFrame(planner_rows)
display(planner_comparison.groupby("treatment").mean(numeric_only=True).round(3))
"""),
md(r"""
## 10. Information-design extension

The scarce object is the High Fee priority position within a two-user match. The baseline action remains binary; there is no continuous bid or seller-revenue rule.

A correlation device recommends one user choose High Fee and the other choose Low Fee. When types differ, it recommends High Fee to the urgent user. When types match, it randomizes the High Fee role. This is a nonbinding coordination signal, not a description of Algorand's deployed fee rule.

The extension varies compliance to determine how accurate a signal must be to reduce same-fee congestion and improve welfare.
"""),
code(r"""
signal_rows = []

for accuracy in np.linspace(0, 1, 11):
    p = deepcopy(P)
    p.signal_accuracy = float(accuracy)

    for seed in range(P.seeds):
        data = run_experiment(seed=seed, treatment="signal", p=p)
        row = summarize(data)
        row.update({"signal_accuracy": accuracy, "seed": seed})
        signal_rows.append(row)

signal_curve = pd.DataFrame(signal_rows).groupby("signal_accuracy").agg(
    same_fee_congestion=("same_fee_congestion", "mean"),
    efficient_type_sorting=("efficient_type_sorting", "mean"),
    mean_total_welfare=("mean_total_welfare", "mean"),
).reset_index()

display(signal_curve.round(3))

fig, ax1 = plt.subplots(figsize=(7.5, 4.2))
ax1.plot(signal_curve["signal_accuracy"], signal_curve["same_fee_congestion"],
         marker="o", label="Same-fee congestion", color="#e64b35")
ax1.plot(signal_curve["signal_accuracy"], signal_curve["efficient_type_sorting"],
         marker="o", label="Efficient type sorting", color="#14877d")
ax1.set_xlabel("Signal-following probability")
ax1.set_ylabel("Rate")
ax1.set_ylim(0, 1.05)
ax1.set_title("Performance of the nonbinding coordination signal")
ax1.legend()
ax1.grid(alpha=0.2)
plt.show()
"""),
md(r"""
## 11. Behavioral game

The future Hugging Face game follows the same one-shot decision structure:

$$
\text{private type + information treatment}
\rightarrow
\text{High Fee / Low Fee}
\rightarrow
\text{payoff and outcome feedback}.
$$

Before choosing, the participant reports:

1. a belief that the other user will choose High Fee;
2. confidence in that belief; and
3. a short explanation of the decision rule.

Treatment 3 additionally displays a nonbinding recommendation. The model benchmark is shown only after the choice. These records can distinguish Bayesian best response from focal choice, ambiguity aversion, level-$k$ reasoning, or reinforcement. No participant observation currently exists.
"""),
md(r"""
## 12. Parameter interpretation

This notebook identifies theoretical and simulated patterns in a stylized fee-choice game; it does not estimate an empirical Algorand equilibrium.

The type prior, payoffs, tremble rate, number of pairs, and signal-following probability are experimental inputs. They must be preregistered, justified, and separated from documented Algorand protocol quantities.

The central planned tests are:

- whether incomplete information increases same-fee congestion relative to complete information;
- whether urgent and patient types sort into High and Low Fee choices;
- whether a coordination signal improves differentiation and welfare; and
- whether results remain robust across type priors, payoff calibrations, and signal compliance.

Any displayed output after execution is a simulated result conditional on these inputs. It should not be described as completed laboratory evidence, a verified protocol result, or a recommendation for Algorand deployment.
"""),
]

assert len(cells) == 28

for index, cell in enumerate(cells):
    cell["id"] = f"cell-{index:02d}"

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
    f.write("\n")

print(OUTPUT)
