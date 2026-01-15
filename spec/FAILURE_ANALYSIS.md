# Failure Analysis and Mitigations

## Purpose
Identify likely failure modes before task execution and adjust the workflow or requirements accordingly.

## Preflight checks (run before PO refinement)
- Requirement clarity: ambiguous scope, missing constraints, unclear UX targets
- Source integrity: broken link, partial content, stale information
- Feasibility: unrealistic deadlines, missing dependencies, incompatible tech
- Testability: acceptance criteria not measurable
- Risk exposure: security, privacy, compliance, operational risk

## Common failure modes
- Ambiguous requirement leads to rework and loopbacks
- Missing acceptance criteria causes QA churn and PO rejection
- No test plan results in late defect discovery
- Parallel task conflicts and merge collisions
- Unclear ownership at milestone gates

## Mitigations
- Force Definition of Ready gate before decomposition
- Auto-generate questions for missing details
- Draft test plan in parallel to catch gaps early
- Add integration test requirements to tasks
- Require explicit owner for each task and gate

