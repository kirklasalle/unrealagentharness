/**
 * UnrealEd 3.0 Agent Cockpit Frontend Controller.
 * Handles WebSocket event streaming, multi-provider chat, action approvals, and live connection testing.
 */

const API_BASE = window.location.origin.includes("http") ? window.location.origin : "http://127.0.0.1:9090";
const WS_BASE = API_BASE.replace(/^http/, "ws") + "/v1/events";

let configData = null;
let chatHistory = [];
let ws = null;

// Initialize on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  initWebSocket();
  loadConfig();
  pollEditorState();
  setInterval(pollEditorState, 3000);

  // Form submission
  document.getElementById("chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    handleUserSubmit();
  });

  // Settings toggle
  document.getElementById("btn-toggle-settings").addEventListener("click", () => {
    const drawer = document.getElementById("sidebar-drawer");
    drawer.style.display = drawer.style.display === "none" ? "flex" : "none";
  });
});

// ---------------------------------------------------------
// WebSocket Event Bus
// ---------------------------------------------------------
function initWebSocket() {
  try {
    ws = new WebSocket(WS_BASE);

    ws.onopen = () => {
      console.log("[WebSocket] Connected to Agent Bridge Event Bus.");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketEvent(data);
      } catch (err) {
        console.error("Failed to parse WS event", err);
      }
    };

    ws.onclose = () => {
      setTimeout(initWebSocket, 2000);
    };
  } catch (e) {
    console.error("WebSocket init error:", e);
  }
}

function handleWebSocketEvent(data) {
  if (data.event === "log_entry" && data.line) {
    appendEngineLog(data.line);
  } else if (data.event === "state_update") {
    updateEditorStatus(data.connected, data.pid);
  }
}

function appendEngineLog(line) {
  const consoleElem = document.getElementById("log-console");
  if (consoleElem) {
    consoleElem.textContent += line + "\n";
    consoleElem.scrollTop = consoleElem.scrollHeight;
  }
}

function clearLogConsole() {
  const consoleElem = document.getElementById("log-console");
  if (consoleElem) consoleElem.textContent = "";
}

// ---------------------------------------------------------
// Editor State Polling
// ---------------------------------------------------------
async function pollEditorState() {
  try {
    const res = await fetch(`${API_BASE}/v1/state`);
    if (res.ok) {
      const data = await res.json();
      updateEditorStatus(data.connected, data.unrealed_pid);
    }
  } catch (e) {
    updateEditorStatus(false, null);
  }
}

function updateEditorStatus(connected, pid) {
  const badge = document.getElementById("editor-status");
  const metricPid = document.getElementById("metric-pid");
  if (connected) {
    badge.className = "status-badge connected";
    badge.innerHTML = `<span class="status-dot"></span><span class="status-text">UnrealEd 3.0 Connected (PID: ${pid || "Active"})</span>`;
    if (metricPid) metricPid.innerText = `Online (PID: ${pid || "Active"})`;
  } else {
    badge.className = "status-badge disconnected";
    badge.innerHTML = `<span class="status-dot"></span><span class="status-text">UnrealEd 3.0 Offline</span>`;
    if (metricPid) metricPid.innerText = "Offline";
  }
}

// ---------------------------------------------------------
// Chat Interaction & Tool Approvals
// ---------------------------------------------------------
async function handleUserSubmit() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  appendUserMessage(text);

  chatHistory.push({ role: "user", content: text });

  // Show thinking indicator
  const thinkingId = appendThinkingIndicator();

  try {
    const res = await fetch(`${API_BASE}/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: chatHistory, auto_execute: false }),
    });

    removeMessage(thinkingId);

    if (res.ok) {
      const data = await res.json();
      chatHistory.push({ role: "assistant", content: data.content });
      appendAssistantMessage(data.content, data.tool_calls);
    } else {
      appendAssistantMessage(`Error from Bridge Server (${res.status}): ${await res.text()}`);
    }
  } catch (err) {
    removeMessage(thinkingId);
    appendAssistantMessage(`Failed to contact Agent Bridge: ${err.message}`);
  }
}

function quickPrompt(text) {
  document.getElementById("chat-input").value = text;
  handleUserSubmit();
}

function appendUserMessage(text) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "message user-message";
  div.innerHTML = `
    <div class="message-avatar">👤</div>
    <div class="message-content">${escapeHtml(text)}</div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
}

function appendThinkingIndicator() {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  const id = "msg-thinking-" + Date.now();
  div.id = id;
  div.className = "message system-message";
  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content"><em>Architect is planning actions and compiling commands...</em></div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendAssistantMessage(content, toolCalls = []) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "message system-message";

  let actionHtml = "";
  if (toolCalls && toolCalls.length > 0) {
    toolCalls.forEach((tc, index) => {
      const actionId = "action-" + Date.now() + "-" + index;
      actionHtml += `
        <div class="action-card" id="${actionId}">
          <div class="action-card-header">
            <span>⚡ PROPOSED ACTION: ${escapeHtml(tc.tool_name)}</span>
          </div>
          <div class="action-card-body">${escapeHtml(JSON.stringify(tc.arguments, null, 2))}</div>
          <div class="action-card-footer">
            <button class="btn btn-primary" onclick="approveToolAction('${actionId}', '${tc.tool_name}', ${escapeAttr(JSON.stringify(tc.arguments))})">
              Approve & Execute
            </button>
          </div>
        </div>
      `;
    });
  }

  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div>${formatMarkdown(content)}</div>
      ${actionHtml}
    </div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
}

async function approveToolAction(cardId, toolName, args) {
  const card = document.getElementById(cardId);
  const footer = card ? card.querySelector(".action-card-footer") : null;
  if (footer) footer.innerHTML = `<em>Executing in UEditorEngine...</em>`;

  try {
    const res = await fetch(`${API_BASE}/v1/tools/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_name: toolName, arguments: args }),
    });

    if (res.ok) {
      const data = await res.json();
      if (footer) footer.innerHTML = `<span class="text-success">✔ Executed Successfully</span>`;
    } else {
      if (footer) footer.innerHTML = `<span style="color: var(--accent-red)">✖ Execution Failed</span>`;
    }
  } catch (err) {
    if (footer) footer.innerHTML = `<span style="color: var(--accent-red)">Error: ${err.message}</span>`;
  }
}

// ---------------------------------------------------------
// Direct Exec & Playtest
// ---------------------------------------------------------
async function executeDirect(cmd) {
  appendUserMessage(`[Command] ${cmd}`);
  try {
    const res = await fetch(`${API_BASE}/v1/exec`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commands: [cmd] }),
    });
    if (res.ok) {
      appendAssistantMessage(`Executed: <code>${escapeHtml(cmd)}</code>`);
    }
  } catch (e) {
    appendAssistantMessage(`Failed to dispatch command: ${e.message}`);
  }
}

async function quickPlaytest() {
  appendUserMessage("Launching Instant Action Playtest in UT2004...");
  try {
    const res = await fetch(`${API_BASE}/v1/game/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ map_name: "Current", game_type: "XGame.xDeathMatch", bots: 3 }),
    });
    if (res.ok) {
      const data = await res.json();
      appendAssistantMessage(`Playtest match launched (PID: ${data.pid || "Active"}). Command: <code>${data.command_line}</code>`);
    }
  } catch (e) {
    appendAssistantMessage(`Playtest launch error: ${e.message}`);
  }
}

// ---------------------------------------------------------
// Configuration & Settings Drawer
// ---------------------------------------------------------
async function loadConfig() {
  try {
    const res = await fetch(`${API_BASE}/v1/config`);
    if (res.ok) {
      configData = await res.json();
      populateProfileDropdown();
      loadSelectedProfile();
    }
  } catch (err) {
    console.error("Failed to load config", err);
  }
}

function populateProfileDropdown() {
  const select = document.getElementById("setting-profile");
  select.innerHTML = "";
  if (!configData || !configData.profiles) return;

  for (const [key, prof] of Object.entries(configData.profiles)) {
    const opt = document.createElement("option");
    opt.value = key;
    opt.innerText = prof.name || key;
    if (key === configData.active_profile) opt.selected = true;
    select.appendChild(opt);
  }
}

function loadSelectedProfile() {
  const profileKey = document.getElementById("setting-profile").value;
  if (!configData || !configData.profiles[profileKey]) return;

  const prof = configData.profiles[profileKey];
  document.getElementById("setting-provider").value = prof.provider || "openai";
  document.getElementById("setting-base-url").value = prof.base_url || "";
  document.getElementById("setting-api-key").value = prof.api_key || "";
  document.getElementById("setting-model").value = prof.model || "";
  document.getElementById("setting-temp").value = prof.temperature || 0.2;
  document.getElementById("temp-val").innerText = prof.temperature || 0.2;
  document.getElementById("setting-tools").checked = prof.enable_tools !== false;
  document.getElementById("setting-vision").checked = prof.enable_vision !== false;

  const metricProf = document.getElementById("metric-profile");
  if (metricProf) metricProf.innerText = prof.name || profileKey;
}

function onProviderChange() {
  const provider = document.getElementById("setting-provider").value;
  const baseUrlInput = document.getElementById("setting-base-url");

  const defaultUrls = {
    google: "https://generativelanguage.googleapis.com/v1beta",
    openai: "https://api.openai.com/v1",
    anthropic: "https://api.anthropic.com/v1",
    ollama: "http://127.0.0.1:11434/v1",
    lmstudio: "http://127.0.0.1:1234/v1",
    groq: "https://api.groq.com/openai/v1",
    deepseek: "https://api.deepseek.com/v1",
    openrouter: "https://openrouter.ai/api/v1",
  };

  baseUrlInput.value = defaultUrls[provider] || "";
}

async function fetchProviderModels() {
  try {
    const res = await fetch(`${API_BASE}/v1/models`);
    if (res.ok) {
      const data = await res.json();
      if (data.models && data.models.length > 0) {
        document.getElementById("setting-model").value = data.models[0];
        alert(`Discovered ${data.models.length} models. Selected: ${data.models[0]}`);
      }
    }
  } catch (err) {
    alert("Could not fetch models: " + err.message);
  }
}

function toggleApiKeyVisibility() {
  const input = document.getElementById("setting-api-key");
  input.type = input.type === "password" ? "text" : "password";
}

// ---------------------------------------------------------
// 5-Step Live Diagnostic Connection Test
// ---------------------------------------------------------
async function testConnection() {
  const btn = document.getElementById("btn-test-connection");
  const badge = document.getElementById("test-result-badge");
  const breakdown = document.getElementById("test-steps-breakdown");

  btn.disabled = true;
  badge.className = "test-badge idle";
  badge.innerText = "Running 5-Step Diagnostic Handshake...";
  breakdown.style.display = "block";
  breakdown.innerHTML = "Executing latency ping and capability checks...";

  const testPayload = {
    profile: {
      provider: document.getElementById("setting-provider").value,
      base_url: document.getElementById("setting-base-url").value,
      api_key: document.getElementById("setting-api-key").value,
      model: document.getElementById("setting-model").value,
      enable_tools: document.getElementById("setting-tools").checked,
      enable_vision: document.getElementById("setting-vision").checked,
    },
  };

  try {
    const res = await fetch(`${API_BASE}/v1/config/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(testPayload),
    });

    const data = await res.json();
    btn.disabled = false;

    if (data.success) {
      badge.className = "test-badge passed";
      badge.innerText = `🟢 Connected (${data.latency_ms}ms) - Ready`;
    } else {
      badge.className = "test-badge failed";
      badge.innerText = `🔴 Test Failed`;
    }

    let stepsHtml = `<strong>Diagnostic Summary:</strong><br>`;
    if (data.steps) {
      for (const [step, status] of Object.entries(data.steps)) {
        const stepName = step.replace(/^\d+_/, "").replace(/_/g, " ").toUpperCase();
        const color = status.includes("Passed") || status.includes("Supported") ? "var(--accent-green)" : "var(--accent-red)";
        stepsHtml += `• ${stepName}: <span style="color: ${color}">${escapeHtml(status)}</span><br>`;
      }
    }
    stepsHtml += `<br><em>${escapeHtml(data.message || "")}</em>`;
    breakdown.innerHTML = stepsHtml;
  } catch (e) {
    btn.disabled = false;
    badge.className = "test-badge failed";
    badge.innerText = `🔴 Connection Error`;
    breakdown.innerHTML = `Failed to contact bridge server: ${escapeHtml(e.message)}`;
  }
}

async function saveSettings() {
  const profileKey = document.getElementById("setting-profile").value;
  if (!configData) configData = { profiles: {} };

  configData.active_profile = profileKey;
  configData.profiles[profileKey] = {
    name: profileKey,
    provider: document.getElementById("setting-provider").value,
    base_url: document.getElementById("setting-base-url").value,
    api_key: document.getElementById("setting-api-key").value,
    model: document.getElementById("setting-model").value,
    temperature: parseFloat(document.getElementById("setting-temp").value),
    max_tokens: 4096,
    enable_tools: document.getElementById("setting-tools").checked,
    enable_vision: document.getElementById("setting-vision").checked,
  };

  try {
    const res = await fetch(`${API_BASE}/v1/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(configData),
    });

    if (res.ok) {
      alert("Configuration saved successfully!");
      loadSelectedProfile();
    }
  } catch (err) {
    alert("Failed to save settings: " + err.message);
  }
}

// ---------------------------------------------------------
// Tab Switching
// ---------------------------------------------------------
function switchTab(tabName) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

  document.getElementById(`tab-${tabName}-btn`).classList.add("active");
  document.getElementById(`tab-${tabName}`).classList.add("active");
}

// Helpers
function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(str) {
  return String(str).replace(/"/g, "&quot;");
}

function formatMarkdown(str) {
  return escapeHtml(str).replace(/\n/g, "<br>");
}
