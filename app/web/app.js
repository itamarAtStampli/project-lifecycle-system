const apiBase = '';
let currentRequirementId = null;

const healthEl = document.getElementById('health');
const startBtn = document.getElementById('startBtn');
const runAgentsBtn = document.getElementById('runAgentsBtn');
const refreshBtn = document.getElementById('refreshBtn');
const nextStateBtn = document.getElementById('nextStateBtn');
const approveBtn = document.getElementById('approveBtn');
const failTestBtn = document.getElementById('failTestBtn');

const timelineList = document.getElementById('timelineList');
const approvalList = document.getElementById('approvalList');
const eventList = document.getElementById('eventList');
const flowMap = document.getElementById('flowMap');
const taskBoard = document.getElementById('taskBoard');
const agentOutput = document.getElementById('agentOutput');

const reqText = document.getElementById('reqText');
const reqTitle = document.getElementById('reqTitle');
const jiraLink = document.getElementById('jiraLink');

const roleSelect = document.getElementById('roleSelect');
const milestoneSelect = document.getElementById('milestoneSelect');
const signedBy = document.getElementById('signedBy');

const states = [
  'Intake',
  'Preflight_Risk_Check',
  'PO_Refinement',
  'Backlog_Ready',
  'Task_Decomposition',
  'In_Development',
  'Code_Review',
  'Integrated',
  'QA_E2E',
  'PO_Acceptance',
  'Release',
  'Done',
];

function setHealth(ok) {
  healthEl.textContent = ok ? 'Online' : 'Offline';
}

async function checkHealth() {
  try {
    const res = await fetch(`${apiBase}/api/health`);
    setHealth(res.ok);
  } catch (err) {
    setHealth(false);
  }
}

async function intake() {
  const payload = {
    title: reqTitle.value || 'Untitled Requirement',
    description: reqText.value,
    jira_link: jiraLink.value || null,
    source: jiraLink.value ? 'jira' : 'text',
  };
  const res = await fetch(`${apiBase}/api/intake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  currentRequirementId = data.id;
  await refreshWorkflow();
}

async function refreshWorkflow() {
  if (!currentRequirementId) return;
  const res = await fetch(`${apiBase}/api/workflow/${currentRequirementId}`);
  const data = await res.json();
  renderTimeline(data.states, data.current_state);
  renderApprovals(data.approvals || []);
  renderEvents(data.events || []);
  renderFlow(data.states, data.current_state, data.events || []);
  renderTasks(data.tasks || []);
  renderAgentOutput(data.requirement || {}, data.agent_outputs || {});
}

function renderTimeline(allStates, currentState) {
  timelineList.innerHTML = '';
  allStates.forEach((state) => {
    const li = document.createElement('li');
    li.textContent = state;
    if (state === currentState) {
      li.style.color = '#f6b26b';
      li.style.fontWeight = '600';
    }
    timelineList.appendChild(li);
  });
}

function renderApprovals(items) {
  approvalList.innerHTML = '';
  items.slice(-8).reverse().forEach((item) => {
    const div = document.createElement('div');
    div.className = 'approval-entry';
    div.textContent = `${item.role} approved ${item.milestone}`;
    approvalList.appendChild(div);
  });
}

function renderEvents(items) {
  eventList.innerHTML = '';
  items.slice(-8).reverse().forEach((item) => {
    const div = document.createElement('div');
    div.className = 'event-entry';
    div.textContent = `${item.type} @ ${new Date(item.ts).toLocaleTimeString()}`;
    eventList.appendChild(div);
  });
}

function renderFlow(allStates, currentState, events) {
  const width = 760;
  const height = 220;
  flowMap.setAttribute('viewBox', `0 0 ${width} ${height}`);
  flowMap.innerHTML = '';

  const cols = 6;
  const rowGap = 90;
  const colGap = 120;
  const startX = 30;
  const startY = 40;

  const nodes = allStates.map((name, index) => {
    const row = Math.floor(index / cols);
    const col = index % cols;
    return {
      name,
      x: startX + col * colGap,
      y: startY + row * rowGap,
    };
  });

  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.innerHTML = `
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
      markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#5c6772"></path>
    </marker>
  `;
  flowMap.appendChild(defs);

  nodes.forEach((node, index) => {
    if (index === nodes.length - 1) return;
    const next = nodes[index + 1];
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', node.x + 70);
    line.setAttribute('y1', node.y + 16);
    line.setAttribute('x2', next.x - 8);
    line.setAttribute('y2', next.y + 16);
    line.setAttribute('stroke', '#5c6772');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('marker-end', 'url(#arrow)');
    flowMap.appendChild(line);
  });

  const loopback = events.some((event) => event.type === 'test.failed');
  if (loopback) {
    const from = nodes.find((node) => node.name === 'QA_E2E');
    const to = nodes.find((node) => node.name === 'In_Development');
    if (from && to) {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${from.x + 50} ${from.y + 10} C ${from.x + 80} ${from.y - 40}, ${to.x - 40} ${to.y - 40}, ${to.x + 10} ${to.y + 10}`);
      path.setAttribute('stroke', '#f6b26b');
      path.setAttribute('stroke-width', '2');
      path.setAttribute('fill', 'none');
      flowMap.appendChild(path);
    }
  }

  nodes.forEach((node) => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', node.x);
    rect.setAttribute('y', node.y);
    rect.setAttribute('rx', '8');
    rect.setAttribute('ry', '8');
    rect.setAttribute('width', '90');
    rect.setAttribute('height', '32');
    rect.setAttribute('fill', node.name === currentState ? '#f6b26b' : '#1a232d');
    rect.setAttribute('stroke', '#2c3946');
    flowMap.appendChild(rect);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', node.x + 45);
    text.setAttribute('y', node.y + 20);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', node.name === currentState ? '#1a1309' : '#c9d1d9');
    text.setAttribute('font-size', '10');
    text.textContent = node.name.replace(/_/g, ' ');
    flowMap.appendChild(text);
  });
}

function renderTasks(tasks) {
  taskBoard.innerHTML = '';
  if (!tasks.length) {
    taskBoard.innerHTML = '<div class=\"hint\">No tasks yet. Run agents to generate tasks.</div>';
    return;
  }
  const lanes = {};
  tasks.forEach((task) => {
    const lane = task.lane || 'Development';
    if (!lanes[lane]) lanes[lane] = [];
    lanes[lane].push(task);
  });

  Object.keys(lanes).forEach((lane) => {
    const laneDiv = document.createElement('div');
    laneDiv.className = 'task-lane';
    const title = document.createElement('h3');
    title.textContent = lane;
    laneDiv.appendChild(title);

    lanes[lane].forEach((task) => {
      const card = document.createElement('div');
      card.className = `task-card ${task.status || 'running'}`;
      card.textContent = `${task.title} (${task.estimate || 'M'})`;
      laneDiv.appendChild(card);
    });

    taskBoard.appendChild(laneDiv);
  });
}

function renderAgentOutput(requirement, outputs) {
  const criteria = requirement.acceptance_criteria || [];
  const risks = requirement.risks || [];
  const dev = outputs.Developer || {};
  const qa = outputs.QATester || {};

  const criteriaHtml = criteria.length
    ? `<div><strong>Acceptance Criteria</strong><div class=\"pill-list\">${criteria.map((c) => `<span class=\"pill\">${c}</span>`).join('')}</div></div>`
    : '<div class=\"hint\">No acceptance criteria yet.</div>';

  const risksHtml = risks.length
    ? `<div><strong>Risks</strong><div class=\"pill-list\">${risks.map((r) => `<span class=\"pill\">${r}</span>`).join('')}</div></div>`
    : '';

  const testCases = dev.test_cases || [];
  const e2e = qa.e2e_tests || [];

  const testsHtml = testCases.length
    ? `<div><strong>Test Cases</strong><div class=\"pill-list\">${testCases.map((t) => `<span class=\"pill\">${t}</span>`).join('')}</div></div>`
    : '';

  const e2eHtml = e2e.length
    ? `<div><strong>E2E Tests</strong><div class=\"pill-list\">${e2e.map((t) => `<span class=\"pill\">${t}</span>`).join('')}</div></div>`
    : '';

  agentOutput.innerHTML = `${criteriaHtml}${risksHtml}${testsHtml}${e2eHtml}`;
}

async function approveMilestone() {
  if (!currentRequirementId) return;
  const payload = {
    requirement_id: currentRequirementId,
    role: roleSelect.value,
    milestone: milestoneSelect.value,
    status: 'approved',
    signed_by: signedBy.value || 'demo_user',
  };
  await fetch(`${apiBase}/api/approval`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  await refreshWorkflow();
}

async function advanceState() {
  if (!currentRequirementId) return;
  const res = await fetch(`${apiBase}/api/workflow/${currentRequirementId}`);
  const data = await res.json();
  const currentIndex = states.indexOf(data.current_state);
  const nextState = states[Math.min(currentIndex + 1, states.length - 1)];
  await fetch(`${apiBase}/api/state`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requirement_id: currentRequirementId, state: nextState }),
  });
  await refreshWorkflow();
}

async function runAgents() {
  if (!currentRequirementId) return;
  await fetch(`${apiBase}/api/agent/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requirement_id: currentRequirementId }),
  });
  await refreshWorkflow();
}

async function failTest() {
  if (!currentRequirementId) return;
  await fetch(`${apiBase}/api/test/fail`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requirement_id: currentRequirementId }),
  });
  await refreshWorkflow();
}

startBtn.addEventListener('click', intake);
runAgentsBtn.addEventListener('click', runAgents);
refreshBtn.addEventListener('click', refreshWorkflow);
nextStateBtn.addEventListener('click', advanceState);
approveBtn.addEventListener('click', approveMilestone);
failTestBtn.addEventListener('click', failTest);

checkHealth();
