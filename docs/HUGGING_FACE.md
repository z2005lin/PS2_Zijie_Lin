# Hugging Face behavioral game

## Open the current artifact

[Fee Coordination Game](https://huggingface.co/spaces/dku-comsci-econ206-2026/SubmitOrWait)

Direct URL:

```text
https://huggingface.co/spaces/dku-comsci-econ206-2026/SubmitOrWait
```

The current public Space was verified on September 27, 2026. The inspected Space revision was `7b3094fad8bc2ce4068d4e95694bf01f6e50390c`.

## What the game implements

- eight independent one-shot rounds;
- private Urgent or Patient transaction types;
- simultaneous High-fee or Low-fee choice;
- baseline incomplete-information and signal conditions;
- Urgent payoffs `(R_H,R_L,R_C)=(8,2,1)`;
- Patient payoffs `(R_H,R_L,R_C)=(5,4,1)`;
- baseline simulated-opponent strategy `Urgent -> H, Patient -> L`;
- pre-choice belief, confidence, and short-reason elicitation;
- post-choice revelation of the other user's hidden type and action;
- congestion, fee differentiation, type sorting, welfare, and planner comparisons; and
- a downloadable session record.

## Relationship to the proposal

The Space implements the proposal's behavioral artifact rather than a deployed Algorand rule. Each round is independent, so the interface does not turn the static model into a repeated dynamic game. The signal is a nonbinding recommendation and does not reveal the other user's private type.

## Privacy and evidence status

The current interface states that no personal information is collected or transmitted. Its co-player choices and reported outcomes are simulated from the model. Any voluntary participant record exported from the interface is not, by itself, a completed laboratory dataset or causal treatment estimate.
