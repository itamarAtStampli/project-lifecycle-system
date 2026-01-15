# Architecture

## Goals
- Orchestrate a full project lifecycle with explicit gates and audit trails.
- Support parallel work where possible while preserving required approvals.
- Provide a UI for intake, status, approvals, and artifact visibility.
- Improve decisions over time using a learning loop.

## High-level components
1. UI
   - Intake form (description or Jira link)
   - Milestone approval screens (role-bound auth)
   - Artifact viewer (PRD, tasks, tests, QA reports, release notes)
   - Audit log and timeline

2. API Gateway
   - Auth (SSO/OAuth)
   - RBAC + milestone approval enforcement
   - Public endpoints for Jira/Git webhooks

3. Workflow Orchestrator
   - Deterministic workflow engine with parallel lanes
   - Agent-as-tool calls for each role
   - Gate checks before state transitions
   - Preflight failure analysis before PO refinement

4. Agent Services (LLM-based)
   - ProductOwner, TeamLead, Developer, CodeReviewer, QATester, ReleaseManager
   - Each has a dedicated SOP and tool permissions

5. Integration Layer
   - Jira: ticket ingestion, field sync, status updates
   - GitHub: PR creation, review status, CI checks
   - Coralogix: logs/metrics/traces, SLA tracking

6. Data Store
   - Requirements, backlog items, tasks, artifacts
   - Decision log and learning memory
   - Audit events and approvals

7. CI/CD & Test Runner
   - Unit + integration tests
   - E2E tests in staging
   - Release promotion to production

## Key design choices
- Workflow pattern for deterministic gates and auditability.
- Parallel execution within stages (task breakdown, dev, documentation, test planning).
- Milestone approvals enforced by RBAC with signed events.
- Learning loop that writes decision data and outcomes for continuous improvement.
- Preflight failure analysis to reduce rework and late-stage surprises.
