# DAWG Plan

## Goal

Build a personal AI assistant that:

- runs on Linux as a background daemon
- is voice-first, but starts with push-to-talk instead of wake word
- is local-first for low-risk and latency-sensitive tasks
- can optionally offload heavier reasoning to online providers later
- supports modular tool and skill additions without a heavy plugin marketplace design
- includes short-term and long-term memory stored locally on disk
- can safely perform tool use and app automation with configurable trust levels

This plan assumes:

- Python is the primary implementation language
- Nix is the primary dev/runtime environment for now
- local inference is done through `llama.cpp` or an OpenAI-compatible local server
- the machine is Linux with an NVIDIA RTX 3060 6 GB GPU

## Product Direction

### Primary interaction model

The assistant should behave like a dormant background service that activates on push-to-talk:

1. user holds a push-to-talk key or button
2. daemon captures microphone audio
3. VAD trims silence and determines segment boundaries
4. STT transcribes with strong bias toward accuracy over absolute lowest latency
5. orchestrator decides whether to:
   - answer directly
   - ask a clarifying question
   - call tools
   - read/write memory
   - draft content
6. assistant responds via TTS
7. daemon returns to dormant state

This is a better v1 than always-listening because it avoids wake-word complexity, reduces accidental triggers, and lowers baseline resource usage.

### Success criteria for the first usable milestone

The first milestone is successful if you can:

- trigger the assistant with push-to-talk from anywhere on your Linux desktop
- say a simple command like "next song" or "pause music" and have it execute reliably
- ask for a drafting task like "write an email to the Georgia Tech admissions office"
- have the assistant ask a clarifying question if required context is missing
- have the assistant save useful facts from the interaction into memory
- hear spoken confirmations such as "drafting one now" and "done drafting, what next"
- end the interaction and have the daemon return to idle

## Non-Goals for v1

Do not build these in the first milestone:

- wake word detection
- multi-agent orchestration beyond a single assistant with optional remote model fallback
- broad desktop automation across every app
- autonomous long-running background actions without confirmation
- complex plugin packaging or external distribution
- high-scale retrieval infrastructure

## Recommended Architecture

Use a layered architecture with hard boundaries between audio, orchestration, tools, memory, and model providers.

### Core modules

#### 1. `dawg-daemon`

Long-running service responsible for:

- lifecycle management
- configuration loading
- hotkey or IPC activation
- audio pipeline coordination
- session management
- logging and health checks

This should be the only always-on process in v1.

#### 2. `audio`

Owns microphone input and output:

- microphone capture
- resampling and normalization
- VAD segmentation
- playback of TTS responses

Keep this isolated from the reasoning loop so audio bugs do not contaminate planning/tool logic.

Submodules:

- `audio.capture`
- `audio.vad`
- `audio.playback`
- `audio.buffers`

#### 3. `speech`

Provider-agnostic wrappers for:

- STT
- TTS

Submodules:

- `speech.stt.base`
- `speech.stt.faster_whisper`
- `speech.tts.base`
- `speech.tts.piper`
- `speech.tts.kokoro` or other higher-quality option later

Reasoning:

- STT accuracy matters most for your use case
- TTS quality matters, but mistakes in TTS are less damaging than STT errors

#### 4. `models`

Abstraction over local and remote reasoning backends.

Submodules:

- `models.base`
- `models.local_llamacpp`
- `models.openai_compat`
- `models.router`

The router chooses between:

- local model for routine commands and simple drafting
- remote provider for heavier reasoning if configured and allowed

This should be policy-driven, not hardcoded.

#### 5. `orchestrator`

The brain of the system.

Responsibilities:

- session state
- prompt assembly
- memory retrieval
- tool planning
- clarification strategy
- trust enforcement
- final response generation

Submodules:

- `orchestrator.session`
- `orchestrator.policy`
- `orchestrator.executor`
- `orchestrator.prompts`
- `orchestrator.response`

This is where "ask if doubtful, otherwise act" should live.

#### 6. `tools`

A local tool runtime for machine actions and app automation.

Examples:

- shell command execution
- media controls
- file reading/writing
- browser open/search
- notification sending
- clipboard access
- app-specific automation adapters

Tool design should be simple:

- each tool has a manifest
- each tool declares inputs, side effects, trust level, and confirmation policy
- each tool returns structured results

Do not start with a general "computer use" agent. Start with explicit tools.

#### 7. `skills`

Lightweight plugin layer above tools and prompts.

A skill should be able to bundle:

- prompt additions or instruction fragments
- memory schemas or retrieval hints
- domain-specific tools
- event hooks
- optional configuration

Example skills:

- music control
- drafting/email
- scheduling
- personal knowledge

Keep the plugin interface file-system based and local. Avoid dynamic install complexity in v1.

#### 8. `memory`

Memory must be a first-class subsystem with separate stores.

Recommended memory categories:

- `working/`: current interaction state and recent context
- `episodic/`: summaries of sessions and completed tasks
- `semantic/`: facts about you, your preferences, recurring entities
- `documents/`: ingested files or reference notes

Recommended disk layout:

```text
memory/
  working/
  episodic/
  semantic/
  documents/
  index/
```

Recommended behavior:

- working memory is cheap and frequently rewritten
- episodic memory stores compact session summaries
- semantic memory stores stable facts with provenance
- document memory supports retrieval over your notes/files later

Do not dump raw transcripts into a single folder and call it memory. That becomes unusable fast.

#### 9. `config`

Centralized configuration for:

- audio devices
- hotkeys
- model providers
- trust policies
- enabled skills
- memory limits
- logging

Use a single main config file plus optional skill-specific config files.

## Speech Stack Recommendation

### VAD

Use `Silero VAD` first since you already depend on it.

Why:

- good quality for local use
- lightweight
- already aligned with your current repo

### STT

Prioritize transcription quality. Recommended order:

1. `faster-whisper` with a strong local model
2. optional remote fallback STT only if local quality is unacceptable

Practical recommendation for your hardware:

- start with `faster-whisper` and test `small` or `medium` depending on latency
- if VRAM pressure is too high, run STT on CPU and keep the GPU for the LLM

Reasoning:

- your tasks are short commands and short drafting prompts
- accuracy matters more than shaving off a few hundred milliseconds
- for simple far-field commands, microphone quality and VAD tuning will matter almost as much as the STT model

### TTS

Start with an offline engine such as `Piper`.

Why:

- local
- fast
- simple to integrate
- good enough for confirmations and follow-up questions

You can upgrade later if you want more natural voices.

## LLM Stack Recommendation

### Local-first model routing

Use a provider-agnostic chat interface with two classes of backends:

- local inference through `llama.cpp`
- remote OpenAI-compatible providers later

This should support:

- structured tool calls
- system prompts
- configurable context assembly
- token streaming

### Model strategy

Use local for:

- media controls
- file tasks
- command routing
- simple drafting
- memory extraction

Allow remote for:

- longer drafting
- complex synthesis
- ambiguous research-heavy work

### Why not fully remote

You explicitly want the core local for direct machine control. That is the right default because:

- lower latency
- fewer privacy concerns
- no hard dependency on network availability
- better fit for a background assistant

## Tooling and Automation Strategy

Treat app automation as tools, not a separate subsystem.

### Initial tool categories

#### Safe low-risk tools

- media key controls
- read calendar file or notes
- draft file creation
- notifications
- clipboard read/write

#### Medium-risk tools

- shell command execution with allowlist or confirmation
- browser navigation
- application launching
- file modification

#### High-risk tools

- destructive shell operations
- bulk file changes
- sending messages/emails
- privileged commands

### Trust model

Each tool should declare:

- `trust_level`: safe, confirm, restricted
- `side_effects`: none, local_state, external_state
- `requires_confirmation`: true or false
- `allowed_when_remote_model`: true or false

Example policy:

- local model may directly execute `safe` tools
- `confirm` tools require spoken or textual confirmation
- `restricted` tools require explicit allowlisting or manual confirmation every time
- remote models should never directly execute dangerous local actions without a local policy gate

This trust boundary matters more than the quality of the prompt.

## Plugin / Skill Design

You do not need a marketplace architecture. Use folder-based plugins.

Recommended shape:

```text
skills/
  music/
    skill.toml
    prompt.md
    tools.py
    hooks.py
  drafting/
    skill.toml
    prompt.md
    memory.py
```

Suggested `skill.toml` fields:

- `name`
- `version`
- `description`
- `enabled`
- `tools`
- `memory_scopes`
- `prompts`
- `events`

Suggested hook points:

- `on_session_start`
- `before_model_call`
- `after_transcript`
- `before_tool_execute`
- `after_tool_execute`
- `before_memory_write`

Keep the runtime API small. If the plugin contract is too flexible early, it will get brittle.

## Memory Design

### Principles

- memory must be useful, not exhaustive
- every stored memory should have a type, timestamp, and provenance
- semantic facts should not be treated the same as transient conversation details
- the system should prefer summaries and extracted facts over raw transcript storage

### Recommended first implementation

#### Working memory

Store:

- current session transcript
- active goals
- open questions
- pending tool outputs

Persistence:

- in memory during the session
- optional short-lived file persistence for crash recovery

#### Episodic memory

Store:

- one concise summary per session
- key completed actions
- unresolved follow-ups

Format:

- JSON or Markdown with metadata

#### Semantic memory

Store:

- stable user preferences
- recurring contacts and institutions
- known context like why you are contacting Georgia Tech

Each semantic item should include:

- fact text
- confidence
- source session
- last confirmed time

#### Document memory

Store:

- imported notes
- reference files
- manually curated personal docs

Later, add embeddings and retrieval. Do not make vector search the first storage primitive for everything.

### Retrieval policy

For each request, retrieve in this order:

1. current session state
2. relevant semantic facts
3. recent episodic summaries
4. document snippets if needed

This is more controllable than blindly stuffing vector search results into every prompt.

## Background Daemon Design

Run the assistant as a single background service with optional clients.

Recommended process model:

- `dawg-daemon`: always running
- `dawg-ctl`: CLI client for status, trigger, debug, config reload
- optional desktop hotkey integration

Potential communication options:

- Unix domain socket
- local HTTP server bound to localhost
- DBus if you want deeper Linux integration later

Recommendation:

Start with a Unix socket or localhost HTTP API. It is simpler to debug than DBus.

## State Machine

The daemon should have explicit states:

- `idle`
- `listening`
- `transcribing`
- `reasoning`
- `awaiting_confirmation`
- `executing_tool`
- `speaking`
- `error`

Why this matters:

- easier debugging
- better logs
- simpler interruption handling
- cleaner recovery from STT/TTS/tool failures

## Confirmation and Clarification Policy

The assistant should prefer clarification over wrong action.

Rules:

- if transcript confidence is low and a tool would cause side effects, ask for confirmation
- if memory contains plausible but stale context, confirm before using it in an external action
- if a command is underspecified, ask one narrow follow-up question
- if a tool is trusted and the intent is unambiguous, act and confirm after

Example:

- "next song" -> execute directly
- "email admissions" -> ask what school if memory is missing or stale
- "delete that folder" -> require confirmation

## Observability

Build debugging in from the beginning.

Include:

- structured logs
- per-stage latency metrics
- transcript confidence logging
- tool execution traces
- memory read/write traces
- session replay artifacts for local debugging

Recommended session artifact layout:

```text
runs/
  2026-05-02T12-34-56/
    transcript.json
    tool_trace.json
    memory_events.json
    final_response.txt
```

Without this, tuning STT, prompts, and tool policies will be guesswork.

## Security and Safety

This is a local assistant with machine control, so safety is mostly a policy and permission problem.

Minimum safeguards:

- explicit trust levels on tools
- confirmation gates for side effects
- allowlist for shell commands in v1
- deny remote models direct unrestricted local execution
- redact secrets from logs
- keep memory storage local by default

Do not rely on the model to "be careful."

## Nix and Packaging Strategy

### Short term

Use Nix for:

- Python environment
- system dependencies
- ffmpeg/audio libs
- reproducible local development

### Medium term

Keep internal packaging Python-native enough that moving to `uv` later is not painful.

That means:

- clean Python package layout
- no Nix-specific assumptions in core runtime code
- config and runtime paths independent of Nix store locations

### Recommendation

Use Nix as the shell/runtime wrapper, not as application architecture.

## Proposed Repository Layout

```text
dawg/
  pyproject.toml
  flake.nix
  plan.md
  src/
    dawg/
      __init__.py
      cli.py
      daemon.py
      config/
      audio/
      speech/
      models/
      orchestrator/
      tools/
      skills/
      memory/
      telemetry/
      state/
  skills/
    music/
    drafting/
  memory/
    working/
    episodic/
    semantic/
    documents/
    index/
  runs/
  tests/
```

Move away from a single top-level `main.py` early.

## Implementation Phases

### Phase 0: Foundations

Goal:

Restructure the repo into a real package and establish configuration, logging, and daemon skeleton.

Deliverables:

- `src/` package layout
- daemon entrypoint
- config system
- structured logging
- basic CLI client
- Nix shell updated for required native deps

Exit criteria:

- daemon starts, idles, and can be pinged via CLI

### Phase 1: Audio and Speech Pipeline

Goal:

Reliable push-to-talk voice input and spoken output.

Deliverables:

- microphone capture module
- Silero VAD integration
- STT provider abstraction
- initial local STT implementation
- TTS provider abstraction
- initial offline TTS implementation
- push-to-talk trigger path

Exit criteria:

- you can trigger speech capture, get transcript text, and hear a spoken reply

### Phase 2: Orchestrator and Session Loop

Goal:

The assistant can conduct a basic interaction loop.

Deliverables:

- session state machine
- prompt assembly
- local model adapter
- local response generation
- clarify-or-act policy

Exit criteria:

- assistant can interpret commands, ask follow-up questions, and return to idle

### Phase 3: Tool Runtime and Trust Policies

Goal:

Reliable local actions with guardrails.

Deliverables:

- tool interface
- tool registry
- trust policy engine
- safe media control tools
- safe file drafting tools
- shell tool with strict policy

Exit criteria:

- assistant can perform trusted actions like music control and safe drafting

### Phase 4: Memory System

Goal:

Useful local memory without retrieval chaos.

Deliverables:

- working, episodic, semantic stores
- memory write policy
- retrieval policy
- session summarization
- fact extraction pipeline

Exit criteria:

- assistant remembers stable facts and uses them correctly in later sessions

### Phase 5: Drafting and Personal Workflow Skills

Goal:

Make the assistant actually useful for your daily workflows.

Deliverables:

- drafting skill
- email/contact memory helpers
- scheduling skill
- richer confirmation flows

Exit criteria:

- assistant can help draft contextual messages and store the relevant personal context

### Phase 6: Remote Provider Fallback

Goal:

Optional heavier reasoning without changing core architecture.

Deliverables:

- OpenAI-compatible provider adapter
- routing policy for local vs remote
- trust boundary rules for remote outputs

Exit criteria:

- remote fallback can improve difficult tasks without gaining unsafe control

## Recommended Technical Choices

### Python libraries

Likely good fits:

- `pyaudio` or a more robust audio I/O library if needed
- `pysilero-vad`
- `faster-whisper`
- `llama-cpp-python` or local server integration
- `pydantic` for config and tool schemas
- `typer` for CLI
- `httpx` for provider integrations
- `sqlite` for some metadata if file-only storage becomes awkward

### Avoid early overengineering with

- Kubernetes-style plugin systems
- event buses for everything
- vector DBs before plain file and metadata storage works
- general GUI automation frameworks as the core abstraction

## Risks and Mitigations

### Risk: STT errors break simple commands

Mitigations:

- prioritize STT quality over minimal latency
- use command confirmation for low-confidence transcriptions
- keep a high-confidence shortcut path for known commands like music controls
- consider constrained intent matching for a small set of critical commands

### Risk: 6 GB VRAM is tight

Mitigations:

- keep components separable so STT can run on CPU if needed
- route simple tasks to smaller local models
- use remote fallback only when beneficial
- avoid keeping too many heavy models resident at once

### Risk: memory becomes noisy and untrustworthy

Mitigations:

- separate semantic facts from transcripts
- store provenance and confidence
- add confirmation for uncertain or stale facts
- summarize sessions instead of storing everything raw

### Risk: tool execution becomes unsafe

Mitigations:

- hard policy gates outside the model
- trust labels per tool
- confirmation workflow
- strict shell allowlist initially

## Immediate Next Build Order

If implementation starts next, the order should be:

1. package restructure from `main.py` into `src/dawg/`
2. daemon skeleton plus CLI control path
3. push-to-talk capture and transcript path
4. TTS reply path
5. local orchestrator loop without tools
6. media control tools
7. drafting tool flow
8. memory subsystem
9. remote provider adapter

This sequence gets you to visible usefulness quickly without locking in bad architecture.

## Open Questions To Resolve During Implementation

These do not block the plan, but they should be decided during execution:

- exact push-to-talk mechanism: global hotkey, terminal keybind, or external button
- whether STT should be fully local at all times or optionally use a remote fallback
- whether media control should target MPRIS first on Linux
- whether email drafting should produce files, clipboard output, or app-specific automation
- whether memory metadata should stay file-based or move partly into SQLite

## Final Recommendation

Build this as a local-first Linux daemon with a strict internal boundary between:

- audio capture
- transcription
- orchestration
- tools
- memory
- model providers

Do not start by building "an AI that can do everything." Start by making one dormant assistant that can:

- hear you through push-to-talk
- transcribe accurately
- control music reliably
- draft messages with clarifying questions
- remember useful facts locally
- return to idle cleanly

If those pieces are clean, everything else becomes an additive system rather than a rewrite.
