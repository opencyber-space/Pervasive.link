import os
import zipfile
import boto3
import tempfile
import json
from botocore.exceptions import BotoCoreError, ClientError


class AssetUploader:
    def __init__(self, bucket_name, region):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region,
        )

    def upload_zip(self, file_path, object_name):
        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name, ExtraArgs={"ACL": "public-read"})
            return f"https://{self.bucket_name}.s3.{self.s3.meta.region_name}.amazonaws.com/{object_name}"
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"S3 Upload failed: {str(e)}")

def process_workflow_zip(file):
    try:
        # Temporary extraction directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "workflow.zip")
            file.save(zip_path)

            # Extract zip
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Load workflow.json
            workflow_json_path = os.path.join(temp_dir, "workflow.json")
            if not os.path.exists(workflow_json_path):
                raise Exception("workflow.json not found in zip")

            with open(workflow_json_path, "r") as f:
                workflow_data = json.load(f)

            # Initialize S3 uploader
            uploader = AssetUploader(bucket_name=os.getenv("AWS_BUCKET_NAME"), region=os.getenv("AWS_REGION"))

            # Process modules
            updated_modules = {}
            for module_name in os.listdir(temp_dir):
                module_path = os.path.join(temp_dir, module_name)
                if os.path.isdir(module_path) and module_name.startswith("module_"):
                    # Zip module directory
                    module_zip_path = os.path.join(temp_dir, f"{module_name}.zip")
                    with zipfile.ZipFile(module_zip_path, "w") as module_zip:
                        for root, _, files in os.walk(module_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, module_path)
                                module_zip.write(file_path, arcname)

                    # Upload to S3 and update codePath
                    s3_url = uploader.upload_zip(module_zip_path, f"modules/{module_name}.zip")
                    module_data = workflow_data["modules"].get(module_name, {})
                    module_data["codePath"] = s3_url
                    updated_modules[module_name] = module_data

            workflow_data["modules"] = updated_modules
            return workflow_data

    except Exception as e:
        raise Exception(f"Error processing workflow zip: {str(e)}")