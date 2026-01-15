# Security and Compliance

## Authentication at milestones
- Every gate requires role-bound approval
- Approvals are signed and recorded
- Multi-factor auth for PO and Release Manager

## Authorization
- RBAC enforced at API and UI layers
- Least privilege for integrations

## Audit
- Immutable audit log of approvals and decisions
- Timestamped with actor identity

## Data handling
- PII redaction in decision logs
- Secrets stored in a secrets manager

