# Provider, Model & Reference Artifact Configuration

The Harness provider configuration is available from **Settings → LLM Providers**. The approved elevation proposal adds explicit provider/model capability badges, connection testing, and separate roles for reference analysis and map execution.

## Provider roles

- **Reference analysis**: image-capable provider used for edge/landmark interpretation and scene-graph review.
- **Map execution**: tool-capable provider allowed to issue UnrealEd commands.
- **Local fallback**: Ollama/compatible local endpoint for private, offline analysis where vision/tool support is available.

API keys remain configuration data and must never be copied into chat history, build manifests, screenshots, or ordinary logs. Attachments are hashed and bounded before being presented to a provider.

See [`PROPOSAL_Valley_Fortress_Vision_UI_Reliability_Elevation.md`](PROPOSAL_Valley_Fortress_Vision_UI_Reliability_Elevation.md) for the approval-gated implementation plan.

# LLM Provider Setup & Top 20 Model Evaluation Guide

## Multi-Provider Model Configuration for Unreal Editor World Creation

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Version:** v2.17.0  
**Target Capabilities:** Procedural 3D Level Architecture, Tool Calling, UnrealScript Coding, and Viewport Vision  

---

## 1. Top 20 Evaluated Models for Unreal Agent Harness

To qualify for autonomous UnrealEd level design, every model must pass the **5 Core Harness Tests**:

1. **Strict Tool / Function Calling**: Flawlessly format JSON parameters for `execute_unrealed_commands`, `create_bsp_room`, `build_outdoor_world`, `build_path_lattice`, and `switch_engine_profile`.
2. **3D Spatial Geometry & Coordinate Math**: Correctly calculate bounding boxes, $+30\text{ UU}$ floor offsets for path nodes, $+50\text{ UU}$ spawn clearances, and jump pad trajectories.
3. **T3D & UnrealScript Syntax Adherence**: Write watertight `.t3d` PolyList polygon windings and correct `.uc` state/function declarations without hallucinated engine classes.
4. **Log Delta Diagnostic & Error Self-Correction**: Parse `Editor.log` / `UnrealEd.log` compiler outputs (detecting embedded pickups, missing textures, or `FPathBuilder` warnings) and formulate immediate in-editor corrective commands.
5. **Multi-Modal Viewport Vision Perception**: Visually inspect the 4-quadrant UnrealEd viewports (Top, Front, Side, 3D Perspective) to detect geometry leaks and lighting misalignments.

---

### 📊 Top 20 Model Tier Matrix (Budget to Frontier)

| Rank | Model Name | Provider / Host | Context | Vision | Cost Tier | Best Use Case in UAH |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 🥇 **1** | **Google Gemini 2.5 Flash** | Google AI Studio | **1M** | ✅ | **Ultra-Budget** | **#1 Overall Recommendation**: Sub-400ms speed, essentially near-free pricing, native tool calling, and instant multi-modal viewport inspection. |
| 🥈 **2** | **Google Gemini 2.5 Flash-Lite** | Google AI Studio | **1M** | ✅ | **Ultra-Budget** | Maximum cost efficiency for rapid continuous command loops and real-time brush manipulation. |
| 🥉 **3** | **DeepSeek V3 (Chat)** | DeepSeek API | **64k** | ❌ | **Ultra-Budget** | Unbeatable text/coding price-to-performance ratio for pure UnrealScript syntax and T3D generation. |
| **4** | **Llama 3.3 70B Versatile** | Groq | **128k** | ❌ | **Ultra-Budget** | Blazing fast inference (250+ tokens/sec on Groq) for instant UnrealEd console command execution. |
| **5** | **Qwen 2.5 Coder 32B** | OpenRouter / Together | **128k** | ❌ | **Ultra-Budget** | Open-weights coding champion with top-tier UnrealScript and C++ structural logic. |
| **6** | **Qwen 2.5 Coder 32B Instruct** | Local (Ollama) | **32k-128k** | ❌ | **100% Free / Offline** | **#1 Local Model**: Flawless T3D grammar, watertight CSG math, and zero internet connection required. |
| **7** | **DeepSeek-Coder-V2.5 (16B/33B)** | Local (Ollama) | **32k** | ❌ | **100% Free / Offline** | Exceptional low-level C++ and UnrealScript bytecode understanding. |
| **8** | **Llama 3.3 70B Instruct** | Local (Ollama) | **32k** | ❌ | **100% Free / Offline** | Massive general knowledge of 25+ years of Unreal Engine history and modding. |
| **9** | **Mistral Small 3 (24B)** | Local (Ollama) | **32k** | ❌ | **100% Free / Offline** | Reliable local function/tool calling with concise, deterministic responses. |
| **10** | **Qwen 2.5 Coder 14B Instruct** | Local (Ollama) | **32k** | ❌ | **100% Free / Offline** | Lightweight option that fits on standard consumer GPUs (RTX 3060/4060) while maintaining solid CSG math. |
| **11** | **Google Gemini 2.5 Pro** | Google AI Studio | **2M** | ✅ | **Mid-Tier** | Unrivaled context capacity: Can ingest entire multi-package `.uc` source trees and build multi-room interconnected compounds. |
| **12** | **OpenAI GPT-4o-mini** | OpenAI | **128k** | ✅ | **Mid-Tier** | Rock-solid schema compliance, fast viewport inspection, and low latency. |
| **13** | **DeepSeek R1 (Reasoner)** | DeepSeek API | **64k** | ❌ | **Mid-Tier** | Extended reasoning chain for complex 3D coordinate trigonometry and JumpPad ballistic calculations. |
| **14** | **Mistral Large 2 (2407)** | Mistral AI | **128k** | ❌ | **Mid-Tier** | High adherence to strict system prompts and multi-stage build pipelines. |
| **15** | **Claude 3.5 Haiku** | Anthropic | **200k** | ❌ | **Mid-Tier** | Ultra-crisp, intelligent tool execution with high instruction following. |
| **16** | **Claude 3.7 Sonnet (Thinking)** | Anthropic | **200k** | ✅ | **Frontier Flagship** | **Top Frontier Model**: Extended thinking mode solves complex multi-tier fortress layouts and intricate UnrealScript replication code without errors. |
| **17** | **OpenAI GPT-4o** | OpenAI | **128k** | ✅ | **Frontier Flagship** | Industry gold standard for multi-modal viewport auditing and function calling. |
| **18** | **OpenAI o3-mini (High)** | OpenAI | **200k** | ❌ | **Frontier Flagship** | Deep algorithmic reasoning for optimizing BSP tree node cuts and navigation reachability lattices. |
| **19** | **Claude 3.5 Sonnet** | Anthropic | **200k** | ✅ | **Frontier Flagship** | Proven architect model for writing complete new Total Conversion game modes. |
| **20** | **OpenAI o1** | OpenAI | **200k** | ✅ | **Frontier Flagship** | Deep conceptual brainstorming, game design documents, and complex architectural mechanics. |

---

## 2. Step-by-Step Provider Setup

### 2.1 Google Gemini 2.5 Flash & Pro (Top Recommendation)

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
- **DeepSeek**: Enter your DeepSeek API key with model `deepseek-chat` or `deepseek-reasoner`.

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

### Diagnostic Status Indicators

* 🟢 **Connected (120ms)**: Ready for full natural language control, tool execution, and vision.
- 🟡 **Connected (No Vision)**: Text and tools work, but viewport screenshot analysis is disabled.
- 🔴 **Error 401**: Invalid API Key.
- 🔴 **Endpoint Unreachable**: Server address incorrect or local Ollama daemon is stopped.
