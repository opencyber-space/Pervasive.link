# DSL Executor SDK

The **DSL Executor SDK** is a Python library for loading and executing declarative, graph-based DSL workflows. It enables both **local** and **remote** execution of modular Python tasks defined as nodes within a Directed Acyclic Graph (DAG), while also supporting advanced routing and orchestration.

This SDK is useful for systems that need to define, version, and execute workflows composed of independently packaged Python modules.

---

## Installation

### Prerequisites

* Python 3.7 or above
* `pip` installed

### From source (local setup)

Clone your project and install the SDK from the root directory:

```bash
cd systems/dsl/dsl_executor
pip install .
```

### For development use (with test dependencies):

```bash
pip install -e .[dev]
```

---

## Usage Example

Assume you have already created and uploaded a DSL workflow using the DSL Creator Server, and it is now registered in your workflow database.

### Step 1: Load and Execute the Workflow

```python
from dsl_executor import new_dsl_workflow_executor, parse_dsl_output

# Set required environment variable or pass the full base URI
WORKFLOWS_API_URL = "http://your-workflow-registry-service"

# Initialize executor from workflow ID
executor = new_dsl_workflow_executor(
    workflow_id="sample_workflow",
    workflows_base_uri=WORKFLOWS_API_URL,
    is_remote=False,          # Set to True for remote execution
    addons={"incr": 2}        # Optional override of globalSettings
)

# Define input to the DSL system
input_data = {
    "user_input": {"x": 10}
}

# Execute the workflow
output = executor.execute(input_data)

# Parse final output or specific module output
print("Final Output:", parse_dsl_output(output))
print("Module 2 Output:", parse_dsl_output(output, module_name="module2"))
```

---

## Module Breakdown

### `DSLWorkflowExecutor` (Abstract Base Class)

Defines the base interface for all executors:

* `execute(input_data)`: Executes the workflow given the input.
* `estimate()`: Placeholder for estimating execution cost/resources.
* `load_modules()`: Optional hook for module setup.

---

### `DSLWorkflowExecutorLocal`

Concrete implementation of `DSLWorkflowExecutor` for local execution.

* Performs topological sorting on the workflow graph
* Uses `LocalCodeExecutor` to:

  * Download or copy module code from `codePath`
  * Install Python dependencies (from `requirements.txt`)
  * Load and invoke `eval()` on each node

---

### `DSLWorkflowExecutorRemote`

Remote execution wrapper. Delegates execution to a remote DSL runtime service using `RemoteDSLExecutor`.

* Requires `POLICIES_SYSTEM_URL` environment variable
* Used for offloading execution to another system or cluster

---

### `new_dsl_workflow_executor(...)`

Factory function to create either a `DSLWorkflowExecutorLocal` or `DSLWorkflowExecutorRemote` instance based on the `is_remote` flag.

#### Arguments:

| Parameter            | Description                                |
| -------------------- | ------------------------------------------ |
| `workflow_id`        | ID of the registered workflow              |
| `workflows_base_uri` | URL of the workflow registry               |
| `is_remote`          | If `True`, creates a remote executor       |
| `addons`             | Dict merged into `globalSettings`          |
| `executor_id`        | Optional unique ID for the remote executor |

---

### `parse_dsl_output(output, module_name="")`

Helper to extract either the final output or a specific module's output from the full DSL result.

* If `module_name` is omitted, returns the final sink node output.
* If provided, returns the output for that specific module.

---
