# Learning Loop

## Objective
Improve agent decision quality over time by capturing inputs, actions, outcomes, and human feedback.

## Data captured
- Stage, input summary, decision taken
- Confidence, reasoning hints (optional), outcome status
- Human overrides and comments
- Metrics (time to complete, defects, rework)
- Failure modes detected and mitigations applied

## Update mechanisms
- Retrieval: use prior similar decisions as context
- Evaluation: score decisions vs outcomes
- Policy update: adjust prompts or routing rules
- Failure pattern mining: identify recurring risk signals

## Guardrails
- Never auto-update prompts without approval
- Keep a rollback log of prompt changes
- Filter sensitive data from long-term memory
