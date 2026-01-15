# Data Model

## Entities
- Requirement
  - id, source (text|jira), title, description, requester, created_at

- SourceDocument
  - id, requirement_id, url, fetched_at, content_hash, extracted_summary

- BacklogItem
  - id, requirement_id, type (epic|story), acceptance_criteria, priority, estimate, status

- Task
  - id, backlog_item_id, owner, estimate, dependencies, status

- Artifact
  - id, type (prd|test_plan|qa_report|release_notes), content, version

- TestResult
  - id, type (unit|integration|e2e), status, coverage, run_at

- PullRequest
  - id, repo, branch, status, approvals, ci_status

- Approval
  - id, role, milestone, status, signed_by, signed_at

- DecisionLog
  - id, stage, input_summary, decision, outcome, confidence, feedback

- Release
  - id, version, environment, status, deployed_at

## Relationships
- Requirement -> BacklogItem (1:n)
- BacklogItem -> Task (1:n)
- Task -> PullRequest (1:1 or 1:n)
- PullRequest -> TestResult (1:n)
- Stage -> Approval (1:n)
- DecisionLog attaches to Requirement/BacklogItem/Task
