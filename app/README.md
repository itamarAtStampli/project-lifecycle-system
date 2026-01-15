# App Scaffold

## Structure
- `backend/server.py` — simple Python HTTP server serving the UI and stub APIs
- `web/` — static UI

## Run locally
```bash
python3 /Users/itamarlev/Documents/ai applications/project-lifecycle-system/app/backend/server.py
```

Then open: http://localhost:8080

## Virtual environment (recommended)
```bash
python3 -m venv /Users/itamarlev/Documents/ai applications/project-lifecycle-system/.venv
source /Users/itamarlev/Documents/ai applications/project-lifecycle-system/.venv/bin/activate
pip install flask boto3
```

## Notes
- This is a dependency-free scaffold with in-memory storage.

## Bedrock agent mode (optional)
This scaffold can call AWS Bedrock to generate acceptance criteria and tasks.

1) Install boto3:
```bash
python3 -m pip install boto3 flask
```

2) Export environment variables:
```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

3) Click **Run Agents (Bedrock)** in the UI after intake.

Note: The backend runs a multi-agent sequence (PO -> Team Lead -> Developer -> QA). Adjust the model ID and payload format to match your chosen model family.

## Jira env loading
If `~/.jira.env` exists, the backend loads it automatically at startup. You can override with:\n
```bash
export ENV_FILE=/path/to/.jira.env
```

## Optional integrations
Jira:
```bash
export JIRA_BASE_URL=https://your-domain.atlassian.net
export JIRA_EMAIL=you@company.com
export JIRA_API_TOKEN=your_token
```

GitHub:
```bash
export GITHUB_REPO=owner/repo
export GITHUB_TOKEN=your_token
```

Coralogix:
```bash
export CORALOGIX_URL=https://your-coralogix-endpoint
export CORALOGIX_API_KEY=your_key
```
