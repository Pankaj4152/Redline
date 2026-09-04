# Redline 🎯

**AI-Powered Pre-Flight Testing & Red-Teaming Tool for AI-Native Coding Assessments**

> *"Does this coding assessment actually produce meaningful engineering signal, or can an AI coding agent solve it without requiring much engineering judgment?"*

---

## 📌 Overview

As software engineers increasingly use AI coding agents (Copilot, Cursor, Gemini Code Assist, Claude Code, etc.), traditional technical coding assessments are becoming obsolete or misleading. A task may appear technically challenging to a human evaluator, yet be trivially solvable by an AI agent given a broad prompt—without the candidate needing to exercise architectural reasoning, system trade-offs, debugging skills, or verification.

**Redline evaluates the assessment itself, not the candidate.**

It analyzes a public GitHub repository and a proposed coding task, simulates different AI-assisted candidate solving strategies, identifies critical signal weaknesses in the task, and recommends concrete modifications to expose true candidate engineering depth.

---


## 🎯 Project Purpose

Redline is being built as a **small, functional proof-of-concept**, not as a production assessment platform.

The project exists to test a specific hypothesis:

> **Before using an AI-native coding assessment to evaluate a candidate, can we automatically stress-test the assessment itself to determine whether it is likely to produce meaningful engineering signal?**

The motivation comes from the changing nature of software engineering.

AI coding agents can increasingly implement features from broad natural-language instructions. This creates a new failure mode for technical assessments:

> A task may appear difficult to a human evaluator while being easy for an AI coding agent to complete with minimal repository understanding, architectural reasoning, or verification.

If that happens, the assessment may fail to distinguish:

* an engineer who understands the system and uses AI effectively
* an engineer who primarily delegates implementation to AI

Redline therefore evaluates the **assessment before the candidate takes it**.

### The Core Product Question

Redline should answer:

> **"If I gave this repository and task to an AI-assisted engineer, would the task force meaningful engineering judgment—or could it be completed mostly through AI delegation?"**

The output should not simply be an arbitrary score.

The system should provide:

1. A concise assessment-health evaluation
2. Evidence explaining why the task does or does not provide strong signal
3. Identification of specific weaknesses
4. Concrete recommendations for improving the task

### What Redline Is NOT

Redline is not intended to be:

* an AI interviewer
* a candidate scoring system
* a recruitment platform
* a browser-based coding environment
* a replacement for Saffron or other assessment platforms
* a fully autonomous coding-agent benchmark
* a scientifically validated assessment-scoring system

It is an **experimental assessment-design and red-teaming tool**.

### MVP Philosophy

The MVP should prioritize:

**Working end-to-end workflow > sophisticated infrastructure**

**Evidence > arbitrary numerical scores**

**Relevant repository context > dumping entire repositories into an LLM**

**Useful recommendations > generic AI-generated criticism**

**Small functional prototype > production SaaS**

The entire workflow should be possible with:

```text
GitHub Repository
+
Assessment Task
        ↓
Repository Context Extraction
        ↓
Assessment Analysis
        ↓
AI-Assisted Strategy Simulation
        ↓
Signal Analysis
        ↓
Evidence
        ↓
Assessment Improvement Recommendations
```

### Important Implementation Constraint

The initial strategy simulator does **not** need to run fully autonomous coding agents.

The three candidate profiles should initially be represented as **structured LLM reasoning simulations**.

Each profile should analyze:

* how it would approach the task
* what repository context it would inspect
* what it would delegate to AI
* what it would likely verify
* what engineering decisions it would make
* what could go wrong

The purpose is to compare the **engineering signal exposed by the assessment**, not to build a complete autonomous coding benchmark.

### Definition of Success

The MVP is successful if a user can provide:

```text
GitHub repository
+
coding assessment
```

and receive a report that makes a technically credible argument about:

> **why this task does or does not require meaningful engineering judgment when AI coding tools are available.**

A good result should contain concrete repository-specific evidence rather than generic statements such as:

> "This task requires problem-solving skills."

Instead, it should say things such as:

> "The task can likely be completed by modifying a single endpoint and does not require understanding the repository's existing service abstraction. No cross-module behavior or non-obvious failure mode is exercised."

The prototype does not need to prove that its scores are objectively correct. It needs to demonstrate that the **red-team workflow itself is useful and technically plausible**.



## 💡 Core Hypothesis

If an AI-native coding assessment can be solved primarily through broad AI delegation without requiring meaningful:
* 🧬 **Repository understanding** (existing abstractions, interfaces, data flow)
* 🏗️ **Architectural reasoning** & design trade-offs
* 🐞 **Debugging & verification**
* 🧪 **Edge-case reasoning** & error resilience

...then the assessment produces **weak engineering signal** about the candidate's actual capability. Redline identifies these weak-signal assessments *before* they are assigned to candidates.

---

## ⚙️ Core Architecture & Pipeline

```text
               ┌──────────────────────────┐
               │    GitHub Repository     │
               │   + Assessment Task      │
               └────────────┬─────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ 1. Repository Analyzer   │
               │   (AST, Module Tree,     │
               │   APIs, Abstractions)    │
               └────────────┬─────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ 2. Assessment Analyzer   │
               │ (Relevance, Impact Scope,│
               │  Architecture Depth)     │
               └────────────┬─────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ 3. Strategy Simulator    │
               │  (3 AI Candidate Models) │
               └──────┬──────┬──────┬─────┘
                      │      │      │
       ┌──────────────┘      │      └──────────────┐
       ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│ AI-Dependent │     │ Naive AI-    │      │ Strong AI-   │
│   Engineer   │     │  Assisted    │      │    Native    │
└──────┬───────┘     └──────┬───────┘      └──────┬───────┘
       │                    │                     │
       └──────────────┬─────┴─────────────────────┘
                      │
                      ▼
               ┌──────────────────────────┐
               │ 4. Assessment Signal     │
               │    Health Analyzer       │
               │  (Scores, Metrics &      │
               │   Evidence Report)       │
               └────────────┬─────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ 5. Recommended           │
               │    Assessment Upgrades   │
               │  (Actionable task tweaks)│
               └──────────────────────────┘
```

---

## 🤖 Simulated Candidate Profiles

Redline evaluates task vulnerability by simulating 3 distinct AI-assisted engineering behaviors:

1. **AI-Dependent Engineer**:
   * *Behavior*: Delegates everything to an AI agent with broad prompts; performs minimal code inspection or edge-case validation.
   * *Risk*: High pass-rate on weak assessments without exercising engineering judgment.
2. **Naive AI-Assisted Engineer**:
   * *Behavior*: Uses AI for quick implementations, makes obvious syntactic fixes, runs superficial happy-path tests, submits.
   * *Risk*: Fails to identify cross-module side effects or architectural constraints.
3. **Strong AI-Native Engineer**:
   * *Behavior*: Inspects repository context, maps dependencies, formulates a precise plan, leverages AI selectively for targeted blocks, rigorously tests failure modes and edge cases.
   * *Outcome*: Exposes true engineering signal when assessments demand deep reasoning.

---

## 📊 Redline Assessment Health Report

Redline generates a comprehensive diagnostic report:

### Evaluated Dimensions
* ⚡ **AI Solvability**: How easily a raw AI prompt can solve the task (High / Medium / Low).
* 🧠 **Reasoning Signal**: Degree of critical engineering judgment demanded.
* 📦 **Repository Depth**: Level of repository architectural context required.
* 🏛️ **Architectural Judgment**: Degree of tradeoff and design decisions needed.
* 🧪 **Verification Requirement**: Necessity of validating non-obvious behavior & edge cases.

### Concrete Task Recommendation Example
* **Original Task**: *"Add CSV export to the analytics endpoint."*
* **Redline Risk Detection**: *Can be completed by modifying a single controller endpoint without understanding data volume, memory limits, or existing streaming response contracts.*
* **Upgraded Task**: *"Add CSV export to the analytics endpoint while preserving the existing streaming response contract and supporting datasets that exceed available RAM."*

---

## 🛠️ Technology Stack

* **Backend**: Python 3.11+, FastAPI, `asyncio`, Pydantic v2
* **AI & LLM Engine**: Gemini API with structured output schemas
* **Analysis**: AST / File Tree Extractor, Code Syntax & Dependency Parsing
* **Frontend**: React, Vite, Modern Dark-Mode Vanilla CSS / Design System
* **Deployment**: Render (Backend), Vercel (Frontend)

---

## 📁 Repository Structure

```text
Redline/
├── backend/                # FastAPI application backend
│   ├── app/
│   │   ├── api/            # API endpoints & routes
│   │   ├── core/           # Configuration & prompt templates
│   │   ├── services/       # Repo analysis, simulation & signal evaluation
│   │   └── main.py         # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/               # React + Vite frontend UI
│   ├── src/                # UI components & visual dashboard
│   ├── package.json        # Frontend dependencies
│   └── README.md           # Frontend documentation
└── README.md               # Main project overview & documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.11+
* Node.js 18+
* Gemini API Key (`GEMINI_API_KEY`)

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📝 Disclaimer

Redline is an experimental prototype designed for stress-testing whether an AI-native coding assessment is likely to produce meaningful engineering signal. It is developed independently using publicly observable software engineering principles.

