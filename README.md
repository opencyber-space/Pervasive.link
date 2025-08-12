# 🚀 DSL Execution & Workflow Orchestration System

**A declarative, distributed system for defining, registering, and executing graph-based AI workflows using Python modules.**
Modular, resource-controlled, and integrated with human-in-the-loop and remote execution capabilities.

### Project Status 🚧

* **Alpha**: This project is in active development and subject to rapid change. ⚠️
* **Testing Phase**: Features are experimental; expect bugs, incomplete functionality, and breaking changes. 🧪
* **Not Production-Ready**: We **do not recommend using this in production** (or relying on it) right now. ⛔
* **Compatibility**: APIs, schemas, and configuration may change without notice. 🔄
* **Feedback Welcome**: Early feedback helps us stabilize future releases. 💬

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
