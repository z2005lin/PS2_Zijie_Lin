# Google Colab notebook

## Open in Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Ox65uxV-g7nPSgpChWZFGmYOfYQTQoCi?usp=sharing)

Direct URL:

```text
https://colab.research.google.com/drive/1Ox65uxV-g7nPSgpChWZFGmYOfYQTQoCi?usp=sharing
```

Access depends on the Google Drive sharing settings selected by the notebook owner.

## Notebook contents

The notebook implements the one-shot static Bayesian fee-choice game described in the proposal:

- symbolic two-user H/L payoff matrix;
- complete-information pure and mixed equilibrium benchmarks;
- type-dependent expected-utility thresholds;
- pure Bayesian best-response checks;
- independent-pair simulations for complete information, incomplete information, and a coordination signal;
- congestion, differentiation, type-sorting, and welfare outcomes;
- sensitivity to the Urgent-type prior and signal-following probability;
- comparisons with random choice and always-H behavioral rules; and
- a planner benchmark for the welfare-maximizing differentiated assignment.

## How to run

1. Open the Colab link.
2. Choose **Runtime -> Run all**.
3. Confirm that every cell completes without an exception.
4. Read the parameter cell before interpreting any table or figure.
5. Treat every numerical output as a conditional simulation result.

The default workflow runs on CPU and does not require an API key.

## Repository copies

- `notebooks/Algorand_PS2_Fee_Choice_Game.ipynb` is the clean source notebook.
- `notebooks/Algorand_PS2_Fee_Choice_Game.executed.ipynb` contains a fresh saved run for inspection.

## Interpretation limit

The notebook solves and simulates a stylized game. It does not estimate a live Algorand equilibrium, validate protocol capacity, or report human-subject treatment effects.
