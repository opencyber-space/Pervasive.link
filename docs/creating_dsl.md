# DSL Policies

---

## Creating a New DSL Node

A **DSL node** is a modular Python component representing a single step in a Directed Acyclic Graph (DAG)-based workflow. Each node encapsulates logic that operates on input data and produces outputs for downstream nodes.

This guide explains how to write and structure a new DSL node.

---

### DSL Node Class Structure

Each DSL node must be implemented as a Python class with the following required interface:

```python
class <NodeClassName>:
    def __init__(self, _name, settings, parameters, global_settings, global_parameters, global_state):
        ...
    
    def eval(self, parameters, input_data, context):
        ...
```

#### Constructor: `__init__`

The constructor initializes the node and receives configuration values from the DSL runtime.

| Parameter           | Description                                                                               |
| ------------------- | ----------------------------------------------------------------------------------------- |
| `_name`             | Reserved for internal use; can be ignored by most implementations                         |
| `settings`          | Node-specific configuration passed at compile time                                        |
| `parameters`        | Per-node parameters passed during runtime                                                 |
| `global_settings`   | Global runtime configuration shared across all nodes                                      |
| `global_parameters` | Additional global values (read-only)                                                      |
| `global_state`      | Mutable state shared across nodes (can be used to maintain global counters, memory, etc.) |

#### Evaluation Method: `eval`

This method contains the actual business logic of the node.

```python
def eval(self, parameters, input_data, context):
    ...
    return result_dict
```

| Parameter    | Description                                                                   |
| ------------ | ----------------------------------------------------------------------------- |
| `parameters` | Same dictionary as passed to the constructor                                  |
| `input_data` | Contains the outputs of previous nodes under `input_data['previous_outputs']` |
| `context`    | Reserved for future use; typically `None`                                     |

The method **must return a dictionary**. This dictionary becomes the output of the node and will be available to downstream nodes.

---

### Example: A Basic Increment Node

The following is a minimal implementation of a node that reads a number from a previous node and increments it using a global setting.

```python
class IncrementNode:
    def __init__(self, _name, settings, parameters, global_settings, global_parameters, global_state):
        self.settings = settings
        self.parameters = parameters
        self.global_settings = global_settings
        self.global_parameters = global_parameters
        self.global_state = global_state

    def eval(self, parameters, input_data, context):
        prev_number = input_data['previous_outputs']['module1']['number']
        increment_by = self.global_settings['incr']

        result = {
            "number": prev_number + increment_by
        }

        return result
```

---

### Directory Layout for a Node

Each node must follow this directory structure:

```
<node-directory>/
├── function.py             # Contains the class implementation
├── requirements.txt        # Optional: Python dependencies
└── (optional files)        # Any additional assets or modules
```

* `function.py` is mandatory and must contain the node class.
* If your logic depends on external packages, list them in `requirements.txt`.

---

### Execution Flow

Nodes are not executed directly. The DSL runtime uses the following process:

1. Downloads or copies the node directory (from a local path or a remote URL).
2. Extracts the archive if necessary (supports `.zip`, `.tar.gz`).
3. Installs dependencies listed in `requirements.txt`.
4. Dynamically loads `function.py` and instantiates the class.
5. Calls the `eval()` method with provided input.

All lifecycle steps are handled by the DSL runtime (`LocalCodeExecutor`), so you only need to focus on your node logic.

---

### Guidelines and Best Practices

* Always return a `dict` from `eval()`.
* Access upstream node outputs via `input_data['previous_outputs']`.
* Validate all required fields before using them.
* Avoid global variables. Use `global_state` for any cross-node memory.
* Keep the node stateless unless state tracking is explicitly needed.
* Class names should be meaningful and versioned when needed (e.g., `MyLogicV1`).

---

### Manual Testing

You can manually test a node by simulating the DSL runtime:

```python
from function import IncrementNode

test_node = IncrementNode(
    _name="increment",
    settings={},
    parameters={},
    global_settings={"incr": 2},
    global_parameters={},
    global_state={}
)

result = test_node.eval({}, {
    "previous_outputs": {
        "module1": {"number": 5}
    }
}, None)

print(result)  # Output: {'number': 7}
```

---

## Defining a DSL Workflow

A DSL workflow describes how multiple Python-based processing modules are connected and executed in a Directed Acyclic Graph (DAG). Each module performs a specific task, and the graph structure defines the execution flow between them.

This section documents how to specify a complete DSL, including the module definitions, graph structure, and runtime parameters.

---

### Workflow Specification Format

A complete DSL workflow is defined as a JSON (or Python dictionary) with the following top-level structure:

```json
{
  "workflow_id": "example_workflow_v1",
  "name": "Example Workflow",
  "version": {
    "version": "1.0",
    "releaseTag": "stable"
  },
  "description": "This is a sample DSL workflow with four connected modules.",
  "tags": ["demo", "example"],
  "globalSettings": { },
  "globalParameters": { },
  "modules": { },
  "graph": { }
}
```

---

### Field-Level Breakdown

| Field                | Type                  | Description                                                              |
| -------------------- | --------------------- | ------------------------------------------------------------------------ |
| `workflow_id`        | `string`              | Unique identifier for the workflow                                       |
| `name`               | `string`              | Human-readable name for the workflow                                     |
| `version.version`    | `string`              | Version number of the workflow                                           |
| `version.releaseTag` | `string`              | Release label (e.g., `beta`, `stable`)                                   |
| `description`        | `string`              | Description of what the workflow does                                    |
| `tags`               | `array of strings`    | Optional tags for search and categorization                              |
| `globalSettings`     | `object`              | Settings available to all modules (e.g., constants, thresholds)          |
| `globalParameters`   | `object`              | Parameters available to all modules (e.g., runtime arguments)            |
| `modules`            | `map<string, Module>` | Keyed by module ID; defines how to load and configure each node          |
| `graph`              | `object`              | Adjacency list representing the DAG; each key maps to downstream modules |

---

### Module Object Structure

Each module is defined in the `modules` field and includes:

| Field                   | Type               | Description                                                |
| ----------------------- | ------------------ | ---------------------------------------------------------- |
| `codePath`              | `string`           | Local file path or remote URL to the module's code package |
| `settings`              | `object`           | Configuration settings specific to the module              |
| `parameters`            | `object`           | Runtime parameters for the module                          |
| `name`                  | `string`           | Descriptive name of the module                             |
| `description`           | `string`           | Explanation of the module’s purpose                        |
| `tags`                  | `array of strings` | Optional tags for searchability                            |
| `resource_requirements` | `object`           | (Optional) Runtime resource hints (e.g., CPU, memory, GPU) |

---

### Graph Field Format

The `graph` field is a directed adjacency list where:

* Each key is a module ID.
* Each value is a list of downstream modules that depend on its output.

> This structure defines the execution order. Nodes with no downstream entries are considered **sink nodes** (final outputs).

---

### Example DSL Definition

```json
{
  "workflow_id": "example_workflow_v1",
  "name": "Simple Arithmetic Workflow",
  "version": {
    "version": "1.0",
    "releaseTag": "stable"
  },
  "description": "A four-module DAG performing a simple arithmetic pipeline.",
  "tags": ["arithmetic", "example"],
  "globalSettings": {
    "incr": 1
  },
  "globalParameters": {},
  "modules": {
    "module1": {
      "codePath": "/path/to/module1",
      "settings": { "module_setting": "value1" },
      "parameters": { "module_param": "value1" },
      "name": "Start Module",
      "description": "Initial input provider",
      "tags": [],
      "resource_requirements": {}
    },
    "module2": {
      "codePath": "/path/to/module2",
      "settings": { "module_setting": "value2" },
      "parameters": { "module_param": "value2" },
      "name": "Left Branch",
      "description": "Processes output from module1",
      "tags": [],
      "resource_requirements": {}
    },
    "module3": {
      "codePath": "/path/to/module3",
      "settings": { "module_setting": "value3" },
      "parameters": { "module_param": "value3" },
      "name": "Right Branch",
      "description": "Processes output from module1",
      "tags": [],
      "resource_requirements": {}
    },
    "module4": {
      "codePath": "/path/to/module4",
      "settings": { "module_setting": "value4" },
      "parameters": { "module_param": "value4" },
      "name": "Merge Output",
      "description": "Aggregates results from module2 and module3",
      "tags": [],
      "resource_requirements": {}
    }
  },
  "graph": {
    "module1": ["module2", "module3"],
    "module2": ["module4"],
    "module3": ["module4"],
    "module4": []
  }
}
```

---

This defines a 4-node workflow:

```
        module1
       /       \
   module2    module3
       \       /
        module4
```

* `module1` is the starting point.
* `module4` is the final output sink.
* Execution order is topologically sorted before execution using the `DSLWorkflowExecutorLocal`.

---

Thanks for the update. Based on your `process_workflow_zip` function, we can infer the **expected packaging structure** for a DSL workflow zip file and document it accordingly.

Below is a **structured documentation** for **packaging a complete DSL workflow archive**, including the expected directory layout, module structure, and upload process.

---

## Packaging a Complete DSL Workflow Archive

This document describes how to package and structure a full DSL workflow, including all modules and a `workflow.json` file, for uploading and processing.

The packaged archive is later uploaded to S3 and parsed using `process_workflow_zip()`, which extracts module directories, zips them individually, uploads them to S3, and rewrites their `codePath` fields in `workflow.json`.

---

### Directory Structure of the Zip Archive

The root of the zip must follow this structure:

```
<your-workflow-name>.zip
├── workflow.json
├── module_module1/
│   ├── function.py
│   └── requirements.txt (optional)
├── module_module2/
│   ├── function.py
│   └── ...
├── module_module3/
│   └── ...
└── module_module4/
    └── ...
```

#### Descriptions

| Item               | Required                 | Description                                           |
| ------------------ | ------------------------ | ----------------------------------------------------- |
| `workflow.json`    | Yes                      | The full DSL workflow definition (same as DSL schema) |
| `module_<name>/`   | Yes                      | Each module directory must be prefixed with `module_` |
| `function.py`      | Yes (inside each module) | Defines the node class                                |
| `requirements.txt` | Optional                 | List of Python dependencies for that module           |

**Important:** Module names in `workflow.json["modules"]` must match the folder names without the `module_` prefix.

---

### workflow\.json Format

Refer to earlier documentation on DSL specification for a full breakdown. Here’s an example minimal structure:

```json
{
  "workflow_id": "sample_workflow",
  "name": "Sample Workflow",
  "version": {
    "version": "1.0",
    "releaseTag": "stable"
  },
  "description": "Simple workflow with four modules.",
  "globalSettings": {
    "incr": 1
  },
  "globalParameters": {},
  "modules": {
    "module1": {
      "codePath": "",  // will be overwritten
      "settings": {},
      "parameters": {},
      "name": "module1",
      "description": "Start node"
    },
    "module2": {
      "codePath": "",
      "settings": {},
      "parameters": {}
    }
    // ... other modules
  },
  "graph": {
    "module1": ["module2"],
    "module2": []
  }
}
```

> The `codePath` for each module will be dynamically replaced with the uploaded S3 URL by the zip processor.

---

### Zipping and Uploading the Archive

1. **Prepare your directory structure** exactly as described.

2. **Create the zip archive**:

```bash
zip -r sample_workflow.zip workflow.json module_module1/ module_module2/ module_module3/ module_module4/
```

3. **Upload the archive using `curl`**:

Once the archive is created, use the following `curl` command to upload it to the DSL Creator Server:

```bash
curl -X POST http://<host>:5000/uploadWorkflow \
  -F "file=@sample_workflow.zip"
```

---

### Example

```bash
curl -X POST http://<host>:5000/uploadWorkflow \
  -F "file=@sample_workflow.zip"
```

---

### Expected Responses

* **Success (HTTP 200):**

```json
{
  "success": true,
  "workflow_id": "sample_workflow",
  "message": "Workflow created successfully"
}
```

* **Client Error (HTTP 400):**
  When no file is provided or if the archive is malformed:

```json
{
  "success": false,
  "message": "No file provided"
}
```

* **Server Error (HTTP 500):**
  When an internal error occurs during processing or S3 upload:

```json
{
  "success": false,
  "message": "Error processing workflow zip: <detailed error message>"
}
```

---

## Complex Workflow Support

While most DSL workflows are expressed as Directed Acyclic Graphs (DAGs), some advanced scenarios require conditional execution, dynamic branching, loops, or routing logic that a static DAG cannot represent.

To support such use cases, the DSL system provides a **router module** mechanism, allowing full control over execution order and logic within a single module.

---

### When to Use a Complex Workflow

Use this approach when:

* You need to introduce **conditional logic** (e.g., `if`, `else`, `switch-case`)
* You want to support **loops**, **retry mechanisms**, or **backtracking**
* Your workflow includes **cycles** or **non-linear execution paths**
* You want a single point of orchestration for **dynamic runtime decisions**

---

### How It Works

Instead of defining a `graph`, you define a **router module** that:

* Receives the DSL input as usual
* Is passed **all loaded module instances**
* Implements custom logic to **invoke modules manually**, in any order

The DSL runtime:

* Loads all modules (including the router)
* Skips normal DAG validation and execution
* Calls the `eval` method of the router module
* The router module has full control over the order and logic of execution

---

### Router Module Signature

```python
class MyRouter:
    def __init__(self, _name, settings, parameters, global_settings, global_parameters, global_state):
        ...

    def eval(self, parameters, input_data, context, all_modules):
        # Manually invoke downstream modules
        result = {}

        # Example: sequential execution
        output1 = all_modules["module1"].eval(parameters, input_data, context)
        input_data["previous_outputs"]["module1"] = output1

        output2 = all_modules["module2"].eval(parameters, input_data, context)
        input_data["previous_outputs"]["module2"] = output2

        # Example: conditional routing
        if output2["score"] > 0.8:
            output3 = all_modules["module3"].eval(parameters, input_data, context)
            input_data["previous_outputs"]["module3"] = output3
            result = output3
        else:
            result = output2

        return result
```

---

## DSL Definition Example

In the `modules` section, define all participating modules including the router:

```json
"modules": {
  "router": {
    "codePath": "/path/to/router",
    "settings": {},
    "parameters": {},
    "name": "router",
    "description": "Controls the entire flow"
  },
  "module1": { ... },
  "module2": { ... },
  "module3": { ... }
}
```

Set the `graph` field to an empty object:

```json
"graph": {}
```

The presence of a module named `router` will trigger complex mode execution.

---

### Runtime Behavior

When the DSL runtime detects a router module:

1. All modules are loaded as usual.
2. The graph is ignored.
3. Only the `eval()` method of the **router module** is called.
4. A fourth argument, `all_modules`, is passed to `eval()` — a dictionary of all module instances keyed by name.
5. The router module is responsible for invoking any or all other modules in the desired order, with the required logic.

---

### Benefits

* Enables execution logic that cannot be represented by DAGs.
* Supports complex stateful or loop-based execution.
* Provides full control to the DSL author without needing framework-level extensions.
* Encourages modular and reusable logic under a unified orchestrator.

---



