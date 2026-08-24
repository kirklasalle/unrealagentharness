# LLM Provider Setup & Live Connection Testing Guide
## Multi-Provider Model Configuration for Unreal Editor World Creation

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Version:** v2.14.0  
**Target Capabilities:** Procedural 3D Level Architecture, Tool Calling, UnrealScript Coding, and Viewport Vision  

---

## 1. Top Recommended Models for Unreal Editor World Creation

Level design and spatial synthesis require strong 3D spatial reasoning, deterministic JSON tool calling, and low latency:

| Model | Provider | Strengths | Speed | Setup Simplicity |
| :--- | :--- | :--- | :---: | :---: |
| 🥇 **Google Gemini 2.5 Flash** | Google AI Studio | **Top Overall**: Sub-400ms speed, 1M context, exceptional JSON tool calling, multi-modal viewport vision. | ⚡ Ultra-Fast | ⭐⭐⭐⭐⭐ (Single API Key) |
| 🥈 **Google Gemini 2.5 Pro** | Google AI Studio | **Deep Architecture**: 2M context, unmatched multi-room reasoning, full package code trees. | 🚀 Fast | ⭐⭐⭐⭐⭐ (Single API Key) |
| 🥉 **Claude 3.7 Sonnet** | Anthropic | **Hybrid Reasoning**: Extended thinking for complex coordinate math & UnrealScript syntax. | 🚀 Fast | ⭐⭐⭐⭐⭐ (Single API Key) |
| **OpenAI GPT-4o** | OpenAI | **Rock-Solid Tool Calling**: Consistent schema execution and standard in-editor commands. | 🚀 Fast | ⭐⭐⭐⭐⭐ (Single API Key) |
| **Llama 3.3 70B (Groq)** | Groq | **Instantaneous**: 300+ tokens/sec for rapid conversational level design. | ⚡ Extreme | ⭐⭐⭐⭐⭐ (Single API Key) |
| **Qwen 2.5 Coder 32B** | Local (Ollama) | **Top Offline Model**: 100% private, zero internet required, exceptional code/T3D syntax. | 💻 Local GPU | ⭐⭐⭐⭐ (One CLI command) |

---

## 2. Step-by-Step Provider Setup

### 2.1 Google Gemini 2.5 Flash & Pro (Recommended)
1. **Get an API Key**: Visit [Google AI Studio](https://aistudio.google.com/) and click **"Create API Key"**.
2. **Configure in UAH**:
   - Open the In-Editor Cockpit -> Click **`⚙️ SETTINGS`**.
   - Select **`Google Gemini 2.5 Flash (Recommended)`** or **`Google Gemini 2.5 Pro`**.
   - Paste your API key into the `API Key` field.
   - Click **`[ ⚡ TEST CONNECTION ]`** $\rightarrow$ Verify green status badge.
   - Click **`[ SAVE ALL SETTINGS ]`**.
3. **Environment Variable Option**:
   ```cmd
   set GEMINI_API_KEY=AIzaSy...
   ```

### 2.2 Anthropic Claude 3.7 Sonnet
1. **Get an API Key**: Visit [Anthropic Console](https://console.anthropic.com/).
2. **Configure in UAH**:
   - In Settings drawer, select **`Anthropic Claude 3.7 Sonnet`**.
   - Paste your `sk-ant-...` API key.
   - Click **`[ ⚡ TEST CONNECTION ]`** $\rightarrow$ Click **`[ SAVE ALL SETTINGS ]`**.

### 2.3 OpenAI GPT-4o
1. **Get an API Key**: Visit [OpenAI Platform](https://platform.openai.com/).
2. **Configure in UAH**:
   - In Settings drawer, select **`OpenAI GPT-4o`**.
   - Paste your `sk-...` API key $\rightarrow$ Test & Save.

### 2.4 High-Speed Groq & DeepSeek
* **Groq**: Enter your Groq API key with model `llama-3.3-70b-versatile` for 300+ tokens/second.
* **DeepSeek**: Enter your DeepSeek API key with model `deepseek-chat` or `deepseek-reasoner`.

### 2.5 100% Offline & Air-Gapped Models (Ollama / Local)
For completely private, offline, zero-cost operation on your local workstation:
1. Download [Ollama](https://ollama.com/).
2. Open terminal and run:
   ```bash
   ollama run qwen2.5-coder:32b
   ```
   *(Or for 16GB GPUs: `ollama run qwen2.5-coder:14b`)*
3. In the UAH Settings drawer, select **`Local Ollama (Offline / Air-Gapped)`**.
4. The Base URL is preset to `http://127.0.0.1:11434/v1`.
5. Click **`[ ⟳ Fetch Models ]`** to automatically load all models installed on your machine.
6. Click **`[ ⚡ TEST CONNECTION ]`** $\rightarrow$ Click **`[ SAVE ALL SETTINGS ]`**.

---

## 3. The 5-Step Live Diagnostic Connection Test

Inside the In-Editor Chat Cockpit Settings drawer, clicking **`[ ⚡ TEST CONNECTION ]`** executes an automated diagnostic handshake:

```
  [Step 1] Network Reachability ──► Checks host DNS and ping
  [Step 2] Authentication Check ──► Validates authorization headers
  [Step 3] Inference Latency    ──► Measures round-trip time in milliseconds (ms)
  [Step 4] Tool-Calling Check   ──► Validates JSON function calling schema support
  [Step 5] Vision Capability    ──► Confirms if model supports PNG viewport inspection
```

### Diagnostic Status Indicators:
* 🟢 **Connected (120ms)**: Ready for full natural language control, tool execution, and vision.
* 🟡 **Connected (No Vision)**: Text and tools work, but viewport screenshot analysis is disabled.
* 🔴 **Error 401**: Invalid API Key.
* 🔴 **Endpoint Unreachable**: Server address incorrect or local Ollama daemon is stopped.
