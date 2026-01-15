# Agents

Each role is implemented as an LLM agent with a dedicated SOP and tool access.

## ProductOwner
- Inputs: requirement or Jira ticket content
- Outputs: refined requirement, acceptance criteria, priority, risks
- Tools: Jira read/write, doc generator

## TeamLead
- Inputs: refined requirement + acceptance criteria
- Outputs: tasks, estimates, dependencies, parallelization plan
- Tools: task planner, Jira write

## Developer
- Inputs: task specification, codebase context
- Outputs: code changes, tests, PR summary
- Tools: repo access, test runner, lint, CI

## CodeReviewer
- Inputs: PR diff, test results, CI status
- Outputs: approve/request changes, review notes
- Tools: GitHub review APIs

## QATester
- Inputs: build artifacts, release notes
- Outputs: E2E test results, defect reports
- Tools: test runner, issue creation

## ReleaseManager
- Inputs: release candidate, QA sign-off, PO acceptance
- Outputs: deployment actions, release notes, rollback plan
- Tools: CI/CD, change management

