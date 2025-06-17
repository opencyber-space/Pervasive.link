from flask import Flask, request, jsonify
import logging

from .k8s import DSLExecutorInitializer, PolicyInterface
from .executor import DSLExecutorClient  
from .db import ExecutorsDB
from .schema import DSLExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

policy_interface = PolicyInterface()


app = Flask(__name__)

@app.route("/dsl-executor/<executor_id>/create-infra", methods=["POST"])
def create_dsl_executor_infra(executor_id):
    try:
        data = request.json
        initializer = DSLExecutorInitializer(
            cluster_config=data["cluster_config"],
            executor_id=executor_id,
            max_processes=data.get("max_processes", 4)  # Default fallback
        )
        initializer.create_executor()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/dsl-executor/<executor_id>/remove-infra", methods=["DELETE"])
def remove_dsl_executor_infra(executor_id):
    try:
        data = request.json
        initializer = DSLExecutorInitializer(
            cluster_config=data["cluster_config"],
            executor_id=executor_id,
            max_processes=data.get("max_processes", 4)
        )
        initializer.remove_executor()
        return jsonify({"success": True, "data": "Removed infra"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/dsl-executor/<executor_id>", methods=["GET"])
def read_dsl_executor(executor_id):
    try:
        executor = ExecutorsDB().read(executor_id)
        if executor:
            return jsonify({"success": True, "data": executor.to_dict()})
        return jsonify({"success": False, "message": "Executor not found."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/dsl-executor/<executor_id>", methods=["PUT"])
def update_dsl_executor(executor_id):
    try:
        data = request.json
        updated_executor = DSLExecutor.from_dict(data)
        success = ExecutorsDB().update(executor_id, updated_executor)
        if success:
            return jsonify({"success": True, "data": "Executor updated successfully."})
        return jsonify({"success": False, "message": "Failed to update executor."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/dsl-executor/<executor_id>", methods=["DELETE"])
def delete_dsl_executor(executor_id):
    try:
        success = ExecutorsDB().delete(executor_id)
        if success:
            return jsonify({"success": True, "data": "Executor deleted successfully."})
        return jsonify({"success": False, "message": "Failed to delete executor."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/dsl-executor/query", methods=["POST"])
def query_dsl_executors():
    try:
        query_filter = request.json
        executors = ExecutorsDB().query(query_filter)
        return jsonify({"success": True, "data": [executor.to_dict() for executor in executors]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/dsl-executor/<executor_id>/execute_dsl", methods=["POST"])
def execute_dsl(executor_id):
    try:
        # Fetch executor
        executor = ExecutorsDB().read(executor_id)
        if not executor:
            return jsonify({"success": False, "message": "Executor not found"}), 404

        base_url = executor.executor_host_uri
        if not base_url:
            return jsonify({"success": False, "message": "Executor host URI not found"}), 400

        client = DSLExecutorClient(ws_url=base_url)

        # Validate request payload
        data = request.json
        dsl_uri = data.get("dsl_uri")
        input_data = data.get("input_data")
        parameters = data.get("parameters", {})

        if not dsl_uri or not input_data:
            return jsonify({
                "success": False,
                "message": "dsl_uri and input_data are required"
            }), 400

        # Execute DSL via WebSocket
        result = client.execute_dsl(dsl_uri, input_data, parameters)
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logging.error(f"Error executing DSL: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/dsl-graph/<executor_id>/estimate", methods=["POST"])
def estimate_dsl_graph(executor_id):
    try:
        data = request.json
        if not data or "policies" not in data:
            return jsonify({"success": False, "message": "Missing 'policies' in request body"}), 400

        policies = data["policies"]
        result = policy_interface.estimate_graph(executor_id, policies)

        return jsonify({"success": True, "data": result})
    except Exception as e:
        logging.error(f"Error estimating DSL graph: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/dsl-graph/<executor_id>/deploy", methods=["POST"])
def deploy_dsl_graph(executor_id):
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Missing JSON payload"}), 400

        policy_interface.deploy_graph(executor_id, data)
        return jsonify({"success": True, "message": "Graph deployed successfully"})
    except Exception as e:
        logging.error(f"Error deploying DSL graph: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def run_server():
    app.run(host=5000)