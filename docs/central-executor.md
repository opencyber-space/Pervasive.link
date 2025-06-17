# DSL Executor & Adhoc Graph API Documentation

## 1. Introduction

The **DSL Executor API system** enables management and execution of dynamic, on-demand (adhoc) DSL-based workflows within a Kubernetes-based infrastructure. It provides endpoints to:

* Deploy and manage executor infrastructure dynamically.
* Register and monitor DSL executors.
* Interact with executor services using REST or WebSocket protocols.
* Estimate and deploy adhoc graphs of DSL functions.

This system supports scale-out execution through Kubernetes and Ambassador, and interfaces with components such as policy databases and graph stores.

---

## 2. DSL Executor Schema

### Definition

```python
from dataclasses import dataclass, field, asdict
from typing import Dict

@dataclass
class DSLExecutor:
    executor_id: str
    executor_host_uri: str
    executor_metadata: Dict
    executor_hardware_info: Dict
    executor_status: str = field(default="healthy")

    @staticmethod
    def from_dict(data: Dict) -> 'DSLExecutor':
        return DSLExecutor(
            executor_id=data['executor_id'],
            executor_host_uri=data['executor_host_uri'],
            executor_metadata=data['executor_metadata'],
            executor_hardware_info=data['executor_hardware_info'],
            executor_status=data.get('executor_status', "healthy"),
        )

    def to_dict(self) -> Dict:
        return asdict(self)
```

### Field Breakdown

| Field Name               | Type   | Default Value | Description                                                                 |
| ------------------------ | ------ | ------------- | --------------------------------------------------------------------------- |
| `executor_id`            | `str`  | required      | Unique identifier for the executor instance. Used as a primary key.         |
| `executor_host_uri`      | `str`  | required      | URI where the executor is reachable. Usually a Kubernetes internal service. |
| `executor_metadata`      | `Dict` | required      | Custom metadata (e.g., environment, version, language runtime, etc.).       |
| `executor_hardware_info` | `Dict` | required      | Hardware configuration (e.g., CPU cores, GPU presence).                     |
| `executor_status`        | `str`  | `"healthy"`   | Health status of the executor (`"healthy"`, `"unhealthy"`, etc.).           |

### Method Descriptions

* `from_dict(data: Dict) -> DSLExecutor`:
  Creates an instance of `DSLExecutor` from a dictionary, assigning a default `"healthy"` status if not provided.

* `to_dict() -> Dict`:
  Converts the `DSLExecutor` instance into a plain dictionary using `asdict()` from the `dataclasses` module.

---

### DSLExecutor

```json
{
  "executor_id": "string",
  "executor_host_uri": "http://executor-service.namespace.svc.cluster.local",
  "executor_metadata": {
    "framework": "Python",
    "version": "1.0.0"
  },
  "executor_hardware_info": {
    "gpu": true,
    "cpu_cores": 8
  },
  "executor_status": "healthy"
}
```

* `executor_id`: Unique identifier for the executor.
* `executor_host_uri`: Service URI used to reach the executor (WebSocket).
* `executor_metadata`: Arbitrary metadata such as runtime environment.
* `executor_hardware_info`: Information about resources like GPU, CPU.
* `executor_status`: Health status (`"healthy"`, `"unhealthy"`).

---

## 3. API Documentation

### 3.1 Executor Infra APIs

#### Create Executor Infrastructure

`POST /dsl-executor/<executor_id>/create-infra`

```json
Request Body:
{
  "cluster_config": { ... },      
  "max_processes": 4              
}
```

Creates a deployment, service, and Ambassador mapping for the executor.

---

#### Remove Executor Infrastructure

`DELETE /dsl-executor/<executor_id>/remove-infra`

```json
Request Body:
{
  "cluster_config": { ... },
  "max_processes": 4
}
```

Tears down all resources associated with the executor.

---

### 3.2 Executor CRUD APIs

#### Get Executor

`GET /dsl-executor/<executor_id>`

Retrieves metadata for the given executor.

---

#### Update Executor

`PUT /dsl-executor/<executor_id>`

```json
Request Body:
{
  "executor_id": "dsl-01",
  "executor_host_uri": "http://...",
  ...
}
```

Updates metadata for the executor.

---

#### Delete Executor

`DELETE /dsl-executor/<executor_id>`

Deletes executor metadata from the registry.

---

#### Query Executors

`POST /dsl-executor/query`

```json
Request Body:
{
  "executor_status": "healthy"
}
```

Returns a list of executors matching the filter.

---

### 3.3 Policy Interface APIs

#### Execute DSL Task

`POST /dsl-executor/<executor_id>/execute_dsl`

```json
Request Body:
{
  "dsl_uri": "workflow://example/echo",
  "input_data": {
    "text": "hello world"
  },
  "parameters": {
    "repeat": 3
  }
}
```

Sends a DSL task to the executor via WebSocket and returns the result.

---

### 3.4 Adhoc Graph APIs

#### Estimate DSL Graph Execution Feasibility

`POST /dsl-graph/<executor_id>/estimate`

```json
Request Body:
{
  "policies": [
    {
      "dsl_uri": "workflow://example/echo",
      "input_data": {...}
    }
  ]
}
```

Estimates where each DSL node can run (based on resources).

---

#### Deploy DSL Graph

`POST /dsl-graph/<executor_id>/deploy`

```json
Request Body:
{
  "graph": { ... },
  "policies": [
    {
      "dsl_uri": "workflow://example/echo",
      "input_data": {...}
    }
  ],
  "deploy_parameters": {
    "workflow://example/echo": {
      "name": "echo-deploy"
    }
  }
}
```

Deploys a DAG-based set of DSL nodes to available infrastructure.

---
