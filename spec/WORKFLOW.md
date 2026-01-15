# Workflow

## Overview
This system uses a deterministic workflow with parallel lanes inside stages. Each stage has required gate conditions and milestone approvals.

## States
1. Intake
2. Preflight_Risk_Check
3. PO_Refinement
4. Backlog_Ready
5. Task_Decomposition
6. In_Development
7. Code_Review
8. Integrated
9. QA_E2E
10. PO_Acceptance
11. Release
12. Done

## Gate rules (milestone approvals)
- Intake -> Preflight_Risk_Check: requirement source validated
- Preflight_Risk_Check -> PO_Refinement: preflight checks completed
- PO_Refinement -> Backlog_Ready: Product Owner approval required
- Code_Review -> Integrated: Code Reviewer approval required + CI green
- QA_E2E -> PO_Acceptance: QA sign-off required + E2E pass
- PO_Acceptance -> Release: Product Owner approval required
- Release -> Done: Release Manager approval required

## Parallel lanes
- Preflight_Risk_Check runs analysis by PO, QA, and Team Lead in parallel
- Task_Decomposition can run in parallel with Test Planning and Documentation Planning
- In_Development can run in parallel by task, with individual subtask status
- QA_E2E can run in parallel with Release Notes preparation

## Loopbacks
- Code_Review -> In_Development (review changes)
- QA_E2E -> In_Development (defect fixes)
- PO_Acceptance -> In_Development (acceptance gaps)

## Stage entry criteria
- Intake: requirement description or Jira link captured
- Preflight_Risk_Check: requirement text extracted and risks assessed
- PO_Refinement: requirement clarified, acceptance criteria drafted
- Backlog_Ready: Definition of Ready satisfied
- Task_Decomposition: tasks and estimates created
- In_Development: task owners assigned
- Code_Review: PR opened and CI pipeline triggered
- Integrated: PR merged to main
- QA_E2E: build promoted to staging and E2E executed
- PO_Acceptance: QA pass, release candidate prepared
- Release: production deployment window approved
- Done: post-release verification completed
