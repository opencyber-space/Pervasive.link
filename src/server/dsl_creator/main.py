from flask import Flask, request, jsonify
from core.utils import process_workflow_zip
from core.db_client import WorkflowsClient
import os

app = Flask(__name__)
client = WorkflowsClient(base_url=os.getenv("WORKFLOWS_API_URL"))


@app.post("/uploadWorkflow")
def upload_workflow():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400

        workflow_file = request.files["file"]
        workflow_data = process_workflow_zip(workflow_file)
        result = client.create_workflow(workflow_data)

        return jsonify(result), 200 if result.get("success") else 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
