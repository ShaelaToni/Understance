# Understance

**Understand before you change.**

You own every line of your software.

Do you know why it works?

Or which line, if changed, will quietly break three other features?

If an AI wrote most of your app, or the person who built it is gone, nobody can tell you. Not with proof.

Understance is being built to. Point it at a Python repository, name the part you want to change, and it will show you what depends on it, how, and why it knows. Every claim will come with the file and the line that prove it. When it cannot see something, it will say so. When your request leaves a real decision open, it will stop and ask you instead of guessing.

Then it will hand you a change brief to take to whatever tool you build with.

It never touches your code. That is not a promise. It is how it is built: nothing in it can write to, edit, or delete your files.

## What it is built to give you

- **The outcome:** understand why your software works, so it can keep working for years after the person who built it has moved on.
- **Proof, not reassurance:** every answer shows the evidence behind it, so you can check it yourself.
- **Speed:** answers in a single run on your own machine, not a multi-week engagement.
- **Almost no effort:** point it at the repository and name the part you want to change. The reading is the tool's job, not yours.

> **Status:** hackathon build, in progress, built in public. The [milestones](#milestones) show exactly what works today and what is still being built.

---

## Why this matters

AI made it easy to build software. It did not make it easy to understand what you built.

That gap is real, and it is growing every day. When the builder leaves, the reasoning leaves too. The next person rebuilds it from guesswork, one nervous change at a time. Code review tools are built for engineering teams on pull requests. Audits are a snapshot that walks out the door with the auditor.

Understance is built for the owner: the person who has to live with the software after everyone else moves on. The goal is simple. Keep the understanding with the system, and keep it current as the system changes.

## How it stays honest (the design)

One rule runs the whole tool: **the model proposes, the system verifies, and every claim traces to evidence.**

- Facts come from reading the code directly (parsing files, mapping imports), not from an AI's opinion.
- The AI model gets one job: explain verified facts in plain language.
- Any claim without evidence behind it gets blocked before you see it.
- Anything out of reach (dynamic imports, generated code, other languages) gets named as a blind spot, never filled with a guess.

This is the design the code is being built to. The milestones show which parts are working today.

## Questions you might be asking

**Is this an AI code audit?**
No. An audit is a one-time verdict. Understance is designed to be a living record of what your system does and why, updated every time it changes.

**Will it change my code?**
No. It reads and explains. You make the change, in your own tool. This is already true of the code: nothing in it can write to your repository.

**Will it run my code?**
No. By design, it reads your files without running them.

**Does my code leave my machine?**
In the setup we build and test with, no. The AI model runs locally on the same computer, and every request returns a receipt showing where the data went. Our first real request (see Milestones) shows `egress: none`: nothing left the machine. If you connect a cloud AI provider instead, the receipt will show that too.

**What can it not do?**
It reveals and traces; it does not certify that code is secure or correct. It does not reach dynamic imports, reflection, generated code, or languages other than Python. It is being built to tell you, on every run, exactly what it could not reach.

**Is it finished?**
No. This is a hackathon build, made in the open: every commit, every recorded decision, and every test is right here in this repository, mistakes included. See the milestones for exactly what works today.

## Milestones

The work, as it happened, in plain English. A box gets checked only when it actually works. No exceptions.

- [x] **Oct 26: Started clean, rules first.** A fresh repository, with the rules for honesty, safety, and build order written down before a single line of code.
- [x] **Oct 26: The core is built and tested.** The basic ideas the whole tool reasons about: what a piece of code is, what depends on what, and what counts as evidence. The tests were written first, then the code that passes them.
- [x] **Oct 26: Swappable by design.** Four plug-in points (the code reader, the data layer, the AI model, and memory) can each be replaced without rewriting the core. Nothing is locked to one vendor.
- [x] **Oct 26: Guardrails that enforce themselves.** An automatic check blocks any commit if the core ever depends on an outside tool. We broke it on purpose to prove it catches the problem.
- [x] **Oct 26: Caught our own mistake, in public.** The practice app did not match its written spec. Instead of letting it slide, we reopened the step and wrote down why. Same honesty the tool is built to give you.
- [x] **Oct 26: Zetaris running locally, answering queries.** The data layer is installed on the build machine and answers SQL.
- [x] **Oct 27: First real AI request through Meterless Nightshift.** Sent from the build Mac and answered by a local model (Qwen 2.5 1.5B) in 2.3 seconds, with a receipt (`rcpt_req_ce9imi24`) and nothing sent off the machine.
- [x] **Oct 27: Practice app matches its spec.** A small synthetic subscription app with one deliberate loop, one untested part, and one open policy question the tool is built to stop and ask you about. Every import in it is checked by hand and pinned by tests.
- [ ] The code reader: turns a repository into verified facts.
- [ ] The agents: plan, retrieve, verify, explain.
- [ ] Nightshift wired in as the tool's AI provider, with every receipt logged.
- [ ] Memory with Meterless H-MEM: decisions and their reasons, kept across sessions.
- [ ] Zetaris Unified Semantic Layer: one view across code facts, change history, and test coverage.
- [ ] One full run, end to end, with every step logged.
- [ ] Demo video and slides.

Automated tests passing today: **40**.

## Setup

Full clean-clone setup gets written as the build lands. What is verified so far:

### Meterless Nightshift (verified Oct 27 on an Apple M1 Pro)

1. Download the free M1 to M4 edition from https://meterless.ai/mac.html ("Free M1+ version").
2. Install it. It is unsigned, so macOS may block the first open: go to **System Settings > Privacy & Security** and choose **Open Anyway**.
3. In Nightshift, open **Setup**, go to **Meterless Local Runtime**, choose **Start runtime**, then download one device model. We use **Qwen 2.5 1.5B** (1.2 GB). No cloud key is needed.
4. Press **Cmd+5** to open the console. It shows the base URL (`http://127.0.0.1:8088/v1`), the auth token, and the default model (`meterless/auto`).
5. Put those three values in a local `.env` file (never committed):

   ```
   METERLESS_BASE_URL=http://127.0.0.1:8088/v1
   METERLESS_RUNTIME_TOKEN=<your auth token>
   METERLESS_MODEL=meterless/auto
   ```

Keep Nightshift's Hotspot mode off, so only apps on your own computer can reach it.

### Zetaris

Installed locally with Docker. Setup steps get added here as the integration lands.

## Usage

Coming with the entry point (`run.py` and `POST /run`), with three sample inputs and their outputs.

## Architecture

Coming as the agents land: the four plug-in points, the facts layer, and the four agents (Planner, Retriever, Evaluator, Explainer).

## Limitations

Stated honestly as the build lands. Today: not production-ready, Python only, and most of the planned pieces are still being built (see Milestones).

## Sponsor technology

- **Zetaris:** the data layer. Installed and answering queries. The Unified Semantic Layer integration is in progress.
- **Meterless:** Nightshift is installed and answered a real request on the build machine (see Milestones). Wiring it in as the tool's AI provider, and building memory with the H-MEM engine, are in progress.
- **Cursor:** not used.
- **NVIDIA:** not used yet. Optional, and may be added through Nightshift if time allows.

## Data

The bundled practice app (`sample_app/`) is **synthetic**: a small subscription service written for this project, inside the build window, to demonstrate the tool. It contains no real customer data and no personal data. It serves as hand-checked ground truth: every dependency in it is verified by hand and pinned by tests.

## AI and model usage

**Models (through Meterless Nightshift):** Qwen 2.5 1.5B, running locally on the build machine. It answered the first verified request. Once wired in, it will turn verified findings into plain-language explanations. By design it will be the only place a model is used; planning, retrieval, and verification run without one.

**Agent framework:** none. The four agents will run on a small custom orchestrator written for this project.

**Sponsor technology:** see [Sponsor technology](#sponsor-technology).

**Development tools:** Built with Claude Code (AI-directed). AI-assisted coding was used for scaffolding, tests, debugging, and documentation. Every change was checked against its tests and the build's review gates before it was committed. This is the single disclosure of the coding tool.

## Third-party code and licences

- pytest: MIT
- ruff: MIT
- pre-commit: MIT

No third-party code is copied into this repository. Additional dependencies are listed here as they are added.
