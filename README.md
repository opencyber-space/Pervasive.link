# 🌐 Pervasive.link: Meta-Protocol for connectivity, interoperability & coordination in the AI Societies.


**Pervasive.link** is a **meta-protocol for agentic interconnection & coordination**. Unlike conventional messaging or orchestration frameworks, it does not enforce a single execution model. Instead, it establishes a semantic, trust-anchored, and execution-neutral connection fabric that binds heterogeneous agents, infrastructures, and workflows into a shared coordination layer. This ensures that **diverse AI & agent architectures can communicate, collaborate, and evolve together without being constrained to a single technical or ideological paradigm**

---

## Why Pervasive.link?

- When multi-agent systems (MAS) mature from isolated deployments into globally networked societies of AIs & Agents, the lack of a unifying coordination layer will be a critical bottleneck.

- Current approaches often remain siloed, relying on localized standards, narrow-purpose protocols, or proprietary integrations that limit scalability, interoperability, and openness. Without a connective infrastructure, MAS ecosystems risk fragmentation, duplication of effort, and fragile trust dynamics.

**Analogy**: Just as TCP/IP allowed disparate networks to converge into the Internet, Pervasive.link provides a universal meta-protocol that allows diverse agents and ecosystems to converge into a planetary-scale society of agents.

**Goal**: Enable interoperability, alignment, and large-scale cooperation across heterogeneous agents and infrastructures.


---

## Core Principles

- **Universality**: any agent/tool/env can speak the same envelope.
- **Semantic grounding**: machine‑readable intents and capabilities, not just bytes.
- **Trust & alignment**: provenance, attestations, and policy bindings travel on‑chain (cryptographically).
- **Transport & execution neutrality**: HTTP, WebSocket, NATS, libp2p, containers, or services.
- **Open‑endedness**: vocabularies, modules, and policies evolve without breaking existing systems.

---

## Two Implementation Paths (You Can Mix Both)

Pervasive.link supports two complementary fronts; choose per context or combine.

### 1) **Spec + Parser**

In this mode, Pervasive.link acts as a front-end specification defining syntax, semantics, and interaction rules. On the back-end, a parser and interpreter enforce these rules as executable workflows, ensuring consistency, interoperability, and reliability—ideal for domains demanding compliance, verification, and determinism.

- **Front end**: machine‑ and human‑readable **specs** (JSON Schema / JSON‑LD).  
- **Back end**: **parser** that generates runtime artifacts such as validators, codecs, routers, and negotiation logic.

**Developer Workflow**  
1. Author/import a spec for a capability.  
2. Run parser → generate validators, language bindings (e.g., Python/Go).  
3. Implement capability logic behind generated interface.  
4. Publish **AdvertiseCapability** referencing content‑addressed schema hashes.  
5. Verify **Receipts** with parser‑generated checkers.

**Example (spec fragment)**

```json
{
  "$id": "pl.schema/Capability.v1",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "provider": { "type": "string" },
    "io": {
      "type": "object",
      "properties": {
        "input": { "type": "array" },
        "output": { "type": "array" }
      },
      "required": ["input", "output"]
    }
  },
  "required": ["id", "provider", "io"]
}
```

**Strengths**: correctness, predictable interop, adoption by API‑centric teams.  
**Tradeoffs**: slower schema evolution, heavier governance for changes.  
**Best for**: regulated/assurance‑heavy domains; large vendor ecosystems.

### 2) **DSL + Workflow**

In this mode, Pervasive.link is expressed as a DSL, enabling agents to declare goals, states, and constraints through flexible constructs. Back-end orchestration engines execute these declarations dynamically, supporting adaptability and open-endedness - deal for evolving ecosystems, innovation networks, and expansive agent societies.

- **Front end**: concise DSL for intents, plans, policies, selection logic.  
- **Back end**: workflow engine compiles to a Task DAG, performs discovery/negotiation, executes, and emits receipts.

**Sketch**

```
goal: SummarizeDocument
inputs:
  doc: cid:doc-123
constraints:
  length: "<400w"
  deadline: "PT30S"
policy:
  require: [cid:pol-PII-no-exfil]
select:
  optimize: [readability:0.6, coverage:0.4, price:0.2]
plan:
  - map: FetchSections(doc)
  - map: Summarize(section)
  - reduce: MergeSummaries()
  - join: AttachReferences()
```

**Strengths**: high expressiveness, fast iteration, great for evolving/open ecosystems.  
**Tradeoffs**: more runtime complexity and observability needs.  
**Best for**: cross‑domain, experimental, federated operator networks.

### Interop Between Paths

- **Spec → DSL**: generate DSL stubs from specs; compose in plans.  
- **DSL → Spec**: stabilize recurring patterns into versioned schemas.  
- **Common substrate**: same envelopes, identity, attestations, receipts, and policies.  
- **Dual discovery**: capability descriptors can reference schema ids and DSL signatures.

---

🚧 **Project Status: Alpha**  
_Not production-ready. See [Project Status](#project-status-) for details._

---

## 📚 Contents 

* [Index](https://pervasive-link-internal.pages.dev/)
* [Central Executor](https://pervasive-link-internal.pages.dev/dsl/central-executor)
* [Creating DSL](https://pervasive-link-internal.pages.dev/dsl/creating_dsl)
* [Registry](https://pervasive-link-internal.pages.dev/dsl/registry)
* [SDK v1](https://pervasive-link-internal.pages.dev/dsl/sdk)
* [SDK v2](https://pervasive-link-internal.pages.dev/dsl/sdk_v2)

---

## 🌟 Highlights

### 🧱 Modular Workflow Architecture

* 🧩 Define and package DSL workflows using versioned, ZIP-based bundles
* ⚙️ DAG-based or router-style execution using Python classes as modular nodes
* 📦 Reusable modules with per-node settings, parameters, and requirements
* 🔁 Supports both simple DAGs and advanced routing logic (loops, conditions)

### 🧠 Intelligent Execution Engine

* 🧠 DSLExecutor SDK for local, multi-process, resource-limited task execution
* 🔌 Addons support for LLMs, webhooks, and callbacks
* ⌛ Task-level CPU, memory, and time enforcement
* 🧍‍♂️ Human intervention support for manual decision points

### 🔍 Registry and Infra Integration

* 🗂️ REST APIs to register, update, query, and delete DSL workflows
* ☁️ Workflow archives are uploaded and unpacked via the Creator Server
* ⚙️ Kubernetes-backed infra provisioning for executor deployment
* 🔄 WebSocket and HTTP APIs to run workflows or execute individual nodes

---

## 📦 Use Cases

| Use Case                      | What It Solves                                                              |
| ----------------------------- | --------------------------------------------------------------------------- |
| **AI Pipeline Orchestration** | Manage modular Python logic as reusable nodes in a DAG or conditional graph |
| **Graph-based DSL Execution** | Execute DSL workflows declaratively with clean separation of logic          |
| **Remote + Local Workflows**  | Load, prepare, and run DSLs across distributed clusters                     |
| **Interactive Workflows**     | Integrate human feedback mid-flow using structured intervention logic       |
| **Versioned Modular Nodes**   | Define, test, and package Python node logic for reuse and distribution      |

---

## 🧩 Integrations

| Component           | Purpose                                         |
| ------------------- | ----------------------------------------------- |
| **MongoDB**         | Metadata storage for registered DSLs            |
| **Flask**           | Creator and Registry API servers                |
| **Redis**           | Workflow state management and output collection |
| **S3/Ceph**         | Workflow ZIP bundle and module storage          |
| **Kubernetes**      | Dynamic provisioning of DSL Executors           |
| **AddonsManager**   | LLM, webhook, and callback integration          |
| **Multiprocessing** | Task-level parallelism with resource control    |

---

## 💡 Why Use This?

| Problem                                        | Our Solution                                                          |
| ---------------------------------------------- | --------------------------------------------------------------------- |
| 🔹 Hard to manage modular AI workflows         | DSL JSON format for workflows with reusable modules                   |
| 🔹 Complex logic orchestration                 | DAG + router mode for conditional/dynamic task flows                  |
| 🔹 No runtime controls for resources           | Enforced CPU/memory/time limits per node                              |
| 🔹 Inconsistent module packaging               | Structured ZIP archive format with `workflow.json` and module folders |
| 🔹 Lack of execution observability and control | State collection and Addons integration                               |

---

## 🛠 Project Status

🟢 **Actively maintained and production-ready**
🧪 Local + remote execution modes
🎛️ Integrated SDK and API layers
📦 Workflow versioning, packaging, and remote execution
🤝 Community feedback and contributions welcome

---

## 📚 DSL System Components

### 🏗 DSL Workflow Definition

* A DSL is defined using `workflow.json` + `module_*/` directories
* Each module contains a `function.py` with a class implementing `eval(...)`
* `workflow.json` describes the graph, settings, and parameters

### 🛠 DSL Registry

* REST API to register, retrieve, update, delete, and query workflows
* MongoDB-backed schema with versioning and DAG structure
* Fully documented schema and API (see docs/)

### 🧪 DSLExecutor SDK

* Resource-isolated multiprocessing executor
* Addons support: LLMs, callbacks, webhooks
* Persistent state and output tracking
* Full Python API (`execute`, `get_task_output`, `persist_outputs`...)

### ☁️ DSL Creator Server

* Upload ZIP with `workflow.json` and `module_*/`
* Server unpacks, uploads modules to S3, rewrites `codePath`
* Sends final DSL to Registry using WorkflowsClient

### ⚙️ DSL Executor Infra APIs

* Provision executors using REST
* Kubernetes deployment + Ambassador ingress
* Execute tasks via HTTP or WebSocket

---


## 🗂️ Key APIs

| Endpoint                                 | Purpose                             |
| ---------------------------------------- | ----------------------------------- |
| `GET /workflows`                         | List all workflows                  |
| `GET /workflows/:workflow_id`            | Get workflow by ID                  |
| `POST /workflows`                        | Create a new DSL workflow           |
| `PUT /workflows/:workflow_id`            | Update workflow                     |
| `DELETE /workflows/:workflow_id`         | Delete workflow                     |
| `POST /workflows/query`                  | Query with dynamic filters          |
| `POST /uploadWorkflow`                   | Upload ZIP archive for registration |
| `POST /dsl-executor/<id>/create-infra`   | Provision an executor               |
| `DELETE /dsl-executor/<id>/remove-infra` | Remove executor infra               |
| `POST /dsl-executor/<id>/execute_dsl`    | Run a DSL task                      |
| `POST /dsl-graph/<id>/estimate`          | Estimate resources for a DSL graph  |
| `POST /dsl-graph/<id>/deploy`            | Deploy an adhoc DSL graph           |

---

# Project Status 🚧

> ⚠️ **Development Status**  
> The project is nearing full completion of version 1.0.0, with minor updates & optimization still being delivered.
> 
> ⚠️ **Alpha Release**  
> Early access version. Use for testing only. Breaking changes may occur.  
>
> 🧪 **Testing Phase**  
> Features are under active validation. Expect occasional issues and ongoing refinements.  
>
> ⛔ **Not Production-Ready**  
> We do not recommend using this in production (or relying on it) right now. 
> 
> 🔄 **Compatibility**  
> APIs, schemas, and configuration may change without notice.  
>
> 💬 **Feedback Welcome**  
> Early feedback helps us stabilize future releases.  



---

## 📢 Communications

1. 📧 Email: [community@opencyberspace.org](mailto:community@opencyberspace.org)  
2. 💬 Discord: [OpenCyberspace](https://discord.gg/W24vZFNB)  
3. 🐦 X (Twitter): [@opencyberspace](https://x.com/opencyberspace)

---

## 🤝 Join Us!

AIGrid is **community-driven**. Theory, Protocol, implementations - All contributions are welcome.

### Get Involved

- 💬 [Join our Discord](https://discord.gg/W24vZFNB)  
- 📧 Email us: [community@opencyberspace.org](mailto:community@opencyberspace.org)
