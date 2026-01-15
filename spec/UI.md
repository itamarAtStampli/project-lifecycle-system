# UI Specification

## Screens
1. Intake
   - Textarea for requirement description
   - Jira link input
   - Submit + validate

2. Project Dashboard
   - Current stage, progress bar, next gate
   - Timeline with state transitions
   - Parallel lanes for tasks

3. Artifacts
   - PRD, acceptance criteria, test plan, QA report, release notes
   - Version history and diff

4. Approvals
   - Milestone checklist
   - Approve/Reject actions with role-based auth

5. Task Board
   - Task list grouped by owner/status
   - Task detail with test results and PR link

6. Audit Log
   - Signed approvals
   - Decision log entries

## Role-based access
- Requester: intake, view status
- PO: refine, approve, view artifacts
- Team Lead: decompose, assign tasks
- Developer: task work, PR submission
- QA: test results, defect filing
- Release Manager: deploy approvals

## UX notes
- Show gate status prominently
- Provide "why" for agent decisions and next actions
- Keep approvals minimal but explicit

