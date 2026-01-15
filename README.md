# Project Lifecycle Orchestrator

A workflow-driven system that mimics a real software development lifecycle (SDLC) with multi-agent collaboration, milestone approvals, and continuous learning from past decisions. The system starts from either a plain-text requirement or a Jira ticket, then orchestrates refinement, task breakdown, development with TDD, code review, QA, product acceptance, and release.

## What's included
- `spec/` design and product documentation
- `sops/` model-ready SOPs for the orchestrator and role agents

## Intended runtime behavior (high level)
1. Intake requirement or Jira ticket link
2. Product Owner refines and defines acceptance criteria
3. Team Lead decomposes into tasks (parallelizable where possible)
4. Developers execute TDD loop on assigned tasks
5. Code review and merge with required approvals
6. QA runs integration + E2E testing
7. Product Owner accepts against criteria
8. Release Manager deploys via CI/CD
9. Learning loop captures decisions and outcomes

## How to use this pack
- Feed `spec/` to humans for alignment.
- Feed `sops/` to an LLM-based controller to execute the lifecycle.
- Use `spec/INTEGRATIONS.md` to wire Jira, GitHub, and Coralogix.

