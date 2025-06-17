import logging
import os
import requests
from kubernetes import client, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DSLExecutorInitializer:
    def __init__(self, cluster_config: dict, executor_id: str, max_processes: int):
        self.executor_id = executor_id
        self.namespace = os.getenv("EXECUTOR_NAMESPACE", "dsl-system")
        self.container_image_name = "agentspacev1/dsl-executor-api:v1"
        self.max_processes = str(max_processes)
        self.deployment_name = f"dsl-executor-{executor_id}"
        self.service_name = f"dsl-executor-svc-{executor_id}"
        self.ambassador_mapping_name = f"dsl-executor-mapping-{executor_id}"

        try:
            self._load_cluster_config(cluster_config)
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.custom_api = client.CustomObjectsApi()
        except Exception as e:
            logger.error(f"Error loading cluster config: {e}")
            raise

    def _load_cluster_config(self, cluster_config):
        config.load_kube_config_from_dict(cluster_config)

    def create_executor(self):
        try:
            self._create_deployment()
            self._create_service()
            self._register_in_ambassador()
        except Exception as e:
            logger.error(f"Error creating DSL executor: {e}")
            raise

    def _create_deployment(self):
        try:
            env_vars = [
                client.V1EnvVar(name="WORKFLOW_URI", value=os.getenv("WORKFLOW_URI")),
            ]

            container = client.V1Container(
                name=self.deployment_name,
                image=self.container_image_name,
                env=env_vars,
                ports=[client.V1ContainerPort(container_port=10250)]
            )

            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": self.deployment_name}),
                spec=client.V1PodSpec(containers=[container])
            )

            spec = client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": self.deployment_name}),
                template=template
            )

            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=self.deployment_name, namespace=self.namespace),
                spec=spec
            )

            self.apps_v1.create_namespaced_deployment(namespace=self.namespace, body=deployment)
            logger.info(f"Deployment {self.deployment_name} created successfully.")
        except Exception as e:
            logger.error(f"Error creating deployment: {e}")
            raise

    def _create_service(self):
        try:
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=self.service_name, namespace=self.namespace),
                spec=client.V1ServiceSpec(
                    selector={"app": self.deployment_name},
                    ports=[client.V1ServicePort(port=10250, target_port=10250, node_port=30900)],
                    type="NodePort"
                )
            )

            self.core_v1.create_namespaced_service(namespace=self.namespace, body=service)
            logger.info(f"Service {self.service_name} created successfully.")
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            raise

    def _register_in_ambassador(self):
        try:
            ambassador_mapping = {
                "apiVersion": "getambassador.io/v2",
                "kind": "Mapping",
                "metadata": {
                    "name": self.ambassador_mapping_name,
                    "namespace": self.namespace
                },
                "spec": {
                    "prefix": f"/dsl-executor/{self.executor_id}",
                    "service": f"{self.service_name}.{self.namespace}.svc.cluster.local:10250",
                },
            }

            self.custom_api.create_namespaced_custom_object(
                group="getambassador.io",
                version="v2",
                namespace=self.namespace,
                plural="mappings",
                body=ambassador_mapping
            )
            logger.info(f"Ambassador mapping {self.ambassador_mapping_name} registered successfully.")
        except Exception as e:
            logger.error(f"Error registering ambassador mapping: {e}")
            raise

    def remove_executor(self):
        try:
            self.apps_v1.delete_namespaced_deployment(name=self.deployment_name, namespace=self.namespace)
            logger.info(f"Deployment {self.deployment_name} deleted successfully.")

            self.core_v1.delete_namespaced_service(name=self.service_name, namespace=self.namespace)
            logger.info(f"Service {self.service_name} deleted successfully.")

            self.custom_api.delete_namespaced_custom_object(
                group="getambassador.io",
                version="v2",
                namespace=self.namespace,
                plural="mappings",
                name=self.ambassador_mapping_name
            )
            logger.info(f"Ambassador mapping {self.ambassador_mapping_name} deleted successfully.")
        except Exception as e:
            logger.error(f"Error removing DSL executor: {e}")
            raise



class PolicyInterface:
    def __init__(self):
        self.base_url = os.getenv("AIOS_POLICY_SYSTEM_URI", "http://localhost:8080").rstrip('/')

    def estimate_graph(self, executor_id: str, policies: list) -> dict:
       
        try:
            url = f"{self.base_url}/graph/estimate-adhoc-graph/{executor_id}"
            response = requests.get(url, json={"policies": policies})
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                raise Exception(data.get("message", "Unknown error during estimate"))
            return data["data"]
        except Exception as e:
            raise Exception(f"Failed to estimate graph: {e}")

    def deploy_graph(self, executor_id: str, data: dict) -> bool:
        
        try:
            url = f"{self.base_url}/graph/deploy-adhoc-graph/{executor_id}"
            response = requests.get(url, json=data)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                raise Exception(data.get("message", "Unknown error during deployment"))
            return True
        except Exception as e:
            raise Exception(f"Failed to deploy adhoc graph: {e}")
