# Reproducibility guide

## Environment

Recommended: Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Fresh notebook run

```bash
jupyter nbconvert \
  --to notebook \
  --execute notebooks/Algorand_PS2_Fee_Choice_Game.ipynb \
  --output Algorand_PS2_Fee_Choice_Game.executed.ipynb \
  --output-dir notebooks \
  --ExecutePreprocessor.timeout=600
```

The main seed is `206`. Sensitivity sections use explicitly listed seed ranges. The notebook prints or stores all model parameters needed to interpret its simulated outputs.

Validate both notebook artifacts with:

```bash
python scripts/validate_notebooks.py
```

## Rebuild the clean notebook

```bash
python scripts/build_fee_choice_notebook.py
```

Run the clean notebook again after rebuilding it.

## Minimal verification checklist

1. Both notebooks contain 28 cells.
2. Every code cell in the executed notebook has an execution count.
3. No code cell contains an error output.
4. The baseline payoffs are Urgent `(8,2,1)` and Patient `(5,4,1)`.
5. The baseline separating strategy is `Urgent -> H, Patient -> L`.
6. Each simulated pair is independent.
7. Every numerical result is labeled simulated rather than empirical.

## Proposal source

The paper can be compiled from `paper/overleaf/main.tex` in an Overleaf project or a compatible local LaTeX installation. The supplied PDF is the submission copy provided with this repository.
