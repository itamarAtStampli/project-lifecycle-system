import argparse
import base64
import json
import os
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, jsonify, request, send_from_directory

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT_DIR, "web")

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")

DATA = {
    "requirements": {},
    "approvals": [],
    "events": [],
    "tasks": {},
    "agent_outputs": {},
}

WORKFLOW_STATES = [
    "Intake",
    "Preflight_Risk_Check",
    "PO_Refinement",
    "Backlog_Ready",
    "Task_Decomposition",
    "In_Development",
    "Code_Review",
    "Integrated",
    "QA_E2E",
    "PO_Acceptance",
    "Release",
    "Done",
]


def load_env_file(path):
    if not path or not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def now_ms():
    return int(time.time() * 1000)


def add_event(event_type, payload):
    event = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "payload": payload,
        "ts": now_ms(),
    }
    DATA["events"].append(event)
    maybe_emit_observability(event)


def maybe_emit_observability(event):
    url = os.environ.get("CORALOGIX_URL")
    api_key = os.environ.get("CORALOGIX_API_KEY")
    if not url or not api_key:
        return
    payload = {
        "eventType": event.get("type"),
        "timestamp": event.get("ts"),
        "payload": event.get("payload"),
    }
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", api_key)
        with urllib.request.urlopen(req, timeout=6):
            pass
    except Exception as exc:
        DATA["events"].append({
            "id": str(uuid.uuid4()),
            "type": "observability.error",
            "payload": {"error": str(exc)},
            "ts": now_ms(),
        })


def jira_issue_key_from_link(link):
    if not link:
        return None
    if "/browse/" in link:
        key = link.split("/browse/")[1].split("?")[0].split("/")[0]
        return key or None
    return None


def jira_request(method, path, payload=None):
    base_url = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not base_url or not email or not token:
        return None
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    auth = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("utf-8")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        add_event("jira.error", {"status": exc.code, "reason": exc.reason})
    except Exception as exc:
        add_event("jira.error", {"error": str(exc)})
    return None


def jira_add_comment(issue_key, text):
    if not issue_key:
        return None
    body = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": text[:3000]}],
            }],
        }
    }
    return jira_request("POST", f"/rest/api/3/issue/{issue_key}/comment", body)


def jira_fetch_issue(issue_key):
    if not issue_key:
        return None
    return jira_request("GET", f"/rest/api/3/issue/{issue_key}?fields=summary,description")


def github_request(method, path, payload=None):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    if not token or not repo:
        return None
    url = "https://api.github.com" + path
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        add_event("github.error", {"status": exc.code, "reason": exc.reason})
    except Exception as exc:
        add_event("github.error", {"error": str(exc)})
    return None


def github_create_issue(title, body):
    repo = os.environ.get("GITHUB_REPO")
    if not repo:
        return None
    response = github_request("POST", f"/repos/{repo}/issues", {"title": title, "body": body})
    if response:
        return response.get("number")
    return None


def github_add_comment(issue_number, body):
    repo = os.environ.get("GITHUB_REPO")
    if not repo or not issue_number:
        return None
    return github_request("POST", f"/repos/{repo}/issues/{issue_number}/comments", {"body": body})


def build_bedrock_body(model_id, prompt):
    if "anthropic" in model_id:
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
    if "titan" in model_id or "amazon" in model_id:
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 800,
                "temperature": 0.2,
            },
        }
    return {
        "prompt": prompt,
        "max_tokens": 800,
        "temperature": 0.2,
    }


def parse_bedrock_text(model_id, payload):
    if "anthropic" in model_id:
        return payload.get("content", [{}])[0].get("text", "")
    if "titan" in model_id or "amazon" in model_id:
        return payload.get("results", [{}])[0].get("outputText", "")
    return payload.get("completion", "")


def call_bedrock(prompt):
    try:
        import boto3  # type: ignore
    except Exception as exc:
        raise RuntimeError("boto3 is not installed") from exc

    model_id = os.environ.get("BEDROCK_MODEL_ID")
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if not model_id or not region:
        raise RuntimeError("Missing BEDROCK_MODEL_ID or AWS_REGION")

    client = boto3.client("bedrock-runtime", region_name=region)
    body = json.dumps(build_bedrock_body(model_id, prompt))
    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    return parse_bedrock_text(model_id, payload)


def extract_json(text):
    if not text:
        raise ValueError("Empty model response")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(cleaned[start:end + 1])


def build_po_prompt(requirement):
    return (
        "You are a Product Owner. "
        "Return JSON only with keys: scope, acceptance_criteria (array), risks (array), clarifying_questions (array). "
        "Be concise and testable.\n\n"
        f"Title: {requirement.get('title')}\n"
        f"Description: {requirement.get('description')}\n"
        f"Source: {requirement.get('source')}\n"
    )


def build_tl_prompt(requirement, po_output):
    return (
        "You are a Team Lead. "
        "Based on the requirement and PO output, return JSON only with keys: "
        "tasks (array of objects with title, lane, estimate, dependencies).\n\n"
        f"Title: {requirement.get('title')}\n"
        f"Description: {requirement.get('description')}\n"
        f"Acceptance Criteria: {po_output.get('acceptance_criteria', [])}\n"
    )


def build_dev_prompt(requirement, tl_output):
    return (
        "You are a Developer. "
        "Return JSON only with keys: test_cases (array), implementation_notes (array). "
        "Focus on TDD-first steps.\n\n"
        f"Title: {requirement.get('title')}\n"
        f"Tasks: {tl_output.get('tasks', [])}\n"
    )


def build_qa_prompt(requirement, tl_output):
    return (
        "You are a QA Engineer. "
        "Return JSON only with keys: e2e_tests (array), qa_risks (array).\n\n"
        f"Title: {requirement.get('title')}\n"
        f"Tasks: {tl_output.get('tasks', [])}\n"
    )


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/workflow/<req_id>")
def workflow(req_id):
    req = DATA["requirements"].get(req_id)
    if not req:
        return jsonify({"error": "not_found"}), 404
    return jsonify({
        "requirement": req,
        "states": WORKFLOW_STATES,
        "current_state": req.get("state", "Intake"),
        "approvals": DATA["approvals"],
        "events": DATA["events"],
        "tasks": DATA["tasks"].get(req_id, []),
        "agent_outputs": DATA["agent_outputs"].get(req_id, {}),
    })


@app.get("/api/events")
def events():
    return jsonify({"events": DATA["events"]})


@app.post("/api/intake")
def intake():
    payload = request.get_json(silent=True) or {}
    req_id = str(uuid.uuid4())
    jira_link = payload.get("jira_link")
    jira_key = jira_issue_key_from_link(jira_link)
    requirement = {
        "id": req_id,
        "source": payload.get("source", "text"),
        "title": payload.get("title", "Untitled Requirement"),
        "description": payload.get("description", ""),
        "jira_link": jira_link,
        "jira_key": jira_key,
        "created_at": now_ms(),
        "state": "Intake",
    }
    if jira_key:
        jira_issue = jira_fetch_issue(jira_key)
        if jira_issue and jira_issue.get("fields", {}).get("summary"):
            requirement["title"] = jira_issue["fields"]["summary"]
    DATA["requirements"][req_id] = requirement
    add_event("intake.created", {"requirement_id": req_id})
    return jsonify({"id": req_id})


@app.post("/api/approval")
def approval():
    payload = request.get_json(silent=True) or {}
    approval_entry = {
        "id": str(uuid.uuid4()),
        "requirement_id": payload.get("requirement_id"),
        "role": payload.get("role"),
        "milestone": payload.get("milestone"),
        "status": payload.get("status", "approved"),
        "signed_by": payload.get("signed_by", "demo_user"),
        "signed_at": now_ms(),
    }
    DATA["approvals"].append(approval_entry)
    add_event("approval.recorded", approval_entry)
    return jsonify({"ok": True})


@app.post("/api/state")
def update_state():
    payload = request.get_json(silent=True) or {}
    req_id = payload.get("requirement_id")
    new_state = payload.get("state")
    if req_id not in DATA["requirements"]:
        return jsonify({"error": "not_found"}), 404
    DATA["requirements"][req_id]["state"] = new_state
    add_event("state.changed", {"requirement_id": req_id, "state": new_state})
    return jsonify({"ok": True})


@app.post("/api/task/update")
def update_task():
    payload = request.get_json(silent=True) or {}
    req_id = payload.get("requirement_id")
    task_id = payload.get("task_id")
    status = payload.get("status")
    tasks = DATA["tasks"].get(req_id, [])
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
    add_event("task.updated", {"requirement_id": req_id, "task_id": task_id, "status": status})
    return jsonify({"ok": True})


@app.post("/api/test/fail")
def test_fail():
    payload = request.get_json(silent=True) or {}
    req_id = payload.get("requirement_id")
    if req_id not in DATA["requirements"]:
        return jsonify({"error": "not_found"}), 404
    DATA["requirements"][req_id]["state"] = "In_Development"
    add_event("test.failed", {"requirement_id": req_id})
    return jsonify({"ok": True})


@app.post("/api/agent/run")
def run_agents():
    payload = request.get_json(silent=True) or {}
    req_id = payload.get("requirement_id")
    req = DATA["requirements"].get(req_id)
    if not req:
        return jsonify({"error": "not_found"}), 404
    try:
        po_output = extract_json(call_bedrock(build_po_prompt(req)))
        add_event("agent.product_owner", {"requirement_id": req_id})

        if req.get("jira_key"):
            jira_add_comment(
                req["jira_key"],
                f"PO output:\nAcceptance Criteria: {po_output.get('acceptance_criteria', [])}\n"
                f"Risks: {po_output.get('risks', [])}\n"
                f"Questions: {po_output.get('clarifying_questions', [])}",
            )

        if not req.get("github_issue_number"):
            issue_body = (
                f"Requirement: {req.get('title')}\n\n"
                f"Acceptance Criteria: {po_output.get('acceptance_criteria', [])}\n"
                f"Risks: {po_output.get('risks', [])}"
            )
            issue_number = github_create_issue(req.get("title", "Requirement"), issue_body)
            if issue_number:
                req["github_issue_number"] = issue_number

        tl_output = extract_json(call_bedrock(build_tl_prompt(req, po_output)))
        add_event("agent.team_lead", {"requirement_id": req_id})

        if req.get("jira_key"):
            jira_add_comment(req["jira_key"], f"Team Lead tasks: {tl_output.get('tasks', [])}")
        if req.get("github_issue_number"):
            github_add_comment(req["github_issue_number"], f"Team Lead tasks: {tl_output.get('tasks', [])}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            dev_future = executor.submit(call_bedrock, build_dev_prompt(req, tl_output))
            qa_future = executor.submit(call_bedrock, build_qa_prompt(req, tl_output))
            dev_output = extract_json(dev_future.result())
            qa_output = extract_json(qa_future.result())
        add_event("agent.developer", {"requirement_id": req_id})
        add_event("agent.qa_tester", {"requirement_id": req_id})

        if req.get("jira_key"):
            jira_add_comment(req["jira_key"], f"Developer test cases: {dev_output.get('test_cases', [])}")
            jira_add_comment(req["jira_key"], f"QA E2E tests: {qa_output.get('e2e_tests', [])}")
        if req.get("github_issue_number"):
            github_add_comment(req["github_issue_number"], f"Developer test cases: {dev_output.get('test_cases', [])}")
            github_add_comment(req["github_issue_number"], f"QA E2E tests: {qa_output.get('e2e_tests', [])}")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    req["acceptance_criteria"] = po_output.get("acceptance_criteria", [])
    risks = po_output.get("risks", []) + qa_output.get("qa_risks", [])
    req["risks"] = list(dict.fromkeys(risks))

    tasks = []
    for item in tl_output.get("tasks", []):
        tasks.append({
            "id": str(uuid.uuid4()),
            "title": item.get("title", "Untitled Task"),
            "lane": item.get("lane", "Development"),
            "estimate": item.get("estimate", "M"),
            "status": "running",
        })
    DATA["tasks"][req_id] = tasks

    DATA["agent_outputs"][req_id] = {
        "ProductOwner": po_output,
        "TeamLead": tl_output,
        "Developer": dev_output,
        "QATester": qa_output,
    }
    add_event("agent.run", {"requirement_id": req_id})

    return jsonify({
        "acceptance_criteria": req["acceptance_criteria"],
        "tasks": tasks,
        "risks": req["risks"],
        "agent_outputs": DATA["agent_outputs"][req_id],
    })


def validate_jira():
    response = jira_request("GET", "/rest/api/3/myself")
    if not response:
        raise RuntimeError("Failed to validate Jira credentials")
    return response.get("displayName")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-jira", action="store_true")
    args = parser.parse_args()

    env_path = os.environ.get("ENV_FILE", os.path.expanduser("~/.jira.env"))
    load_env_file(env_path)

    if args.validate_jira:
        name = validate_jira()
        print(f"Jira credentials valid for: {name}")
        return

    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Serving UI on http://{host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
