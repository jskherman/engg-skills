# DAG Vocabulary for Process Data

## Confounder

A variable that causes both the treatment and the outcome. Failing to
adjust for it biases the estimated treatment effect.

Example (LPG sulfur problem): FCC/DCU source split is a common cause of
both the blended heavy-end balance and the product sulfur (through the
sulfur severity of each source). Adjusting for source split is required to
isolate a treating-unit effect.

## Mediator

A variable on the causal path between treatment and outcome. Adjusting for
it blocks part of the effect you are trying to estimate; do NOT include
mediators in a total-effect adjustment set.

Example: rich amine loading is a mediator between absorber acid-sulfur load
and product H2S. For the total effect of feed sulfur on product sulfur, do
not adjust for rich loading.

## Collider

A variable caused by both the treatment and the outcome (or by ancestors
of both). Adjusting for a collider opens a non-causal path and induces
spurious dependence.

Example: a "operator intervention" indicator that fires when both heavy
ends are rising AND sulfur is rising is a collider; conditioning on it can
make heavy-end and sulfur look unrelated within the unaffected window.

## Back-door criterion

A set Z satisfies the back-door criterion relative to (treatment T,
outcome Y) if:
1. No node in Z is a descendant of T.
2. Z blocks every back-door path from T to Y (i.e., every path starting
   with an arrow into T).

The parents of T always satisfy the back-door criterion in a DAG (under
no latent confounding). The script's `backdoor_adjustment` returns that
set and verifies the criterion explicitly.

## d-separation

Two sets X and Y are d-separated by Z if every path between them is
blocked by Z. Pearl's algorithm: build the ancestral subgraph of X ∪ Y ∪ Z,
moralise it (marry parents), remove Z, and check connectivity.

## Adjustment sets in regression

A total-effect estimator regresses Y on T and Z (a back-door adjustment
set). A mediator-controlled estimator that includes mediators gives the
direct effect (not the total effect). Always document which estimand the
regression targets.
