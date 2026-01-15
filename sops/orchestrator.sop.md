# SOP: Workflow Orchestrator

## Purpose
Run the project lifecycle deterministically with parallel lanes, milestone approvals, and auditable artifacts.

## Inputs
- Requirement text OR Jira ticket link

## Outputs
- Final release record with approvals and artifacts

## Steps
1. Intake
   - If Jira link provided, fetch ticket details.
   - If text provided, create a new Requirement.

2. Preflight Risk Check
   - Validate requirement source content.
   - Identify ambiguity, feasibility, and testability risks.
   - If issues found, generate clarifying questions.

3. PO Refinement
   - Call ProductOwner agent to clarify scope and draft acceptance criteria.
   - Require PO approval to advance.

4. Task Decomposition
   - Call TeamLead agent to create tasks, estimates, dependencies.
   - Create parallel lanes for independent tasks.

5. Development (parallel)
   - Assign tasks to Developer agents.
   - Enforce TDD loop: tests -> code -> refactor.

6. Code Review
   - Require CI green and CodeReviewer approval.
   - Loop back to development on request changes.

7. QA E2E
   - Call QATester to run E2E suite.
   - Loop back to dev on failures.

8. PO Acceptance
   - Call ProductOwner to verify acceptance criteria.
   - Require approval to proceed.

9. Release
   - Call ReleaseManager to deploy and record release notes.
   - Require ReleaseManager approval.

10. Learning
   - Log decisions, outcomes, and feedback.

## Gate checks
- Require role-based auth approvals at each milestone.
- Do not progress if required approvals or tests are missing.
