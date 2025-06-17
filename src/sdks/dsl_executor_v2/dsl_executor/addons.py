from typing import Callable, Dict, Any, Optional
import requests


class DSLInferenceAddon:
    def __init__(self, name: str, inference_api):
        self.name = name
        self.inference_api = inference_api

    def run_inference(self, input_data: Dict[str, Any]) -> str:
        
        return self.inference_api.run_inference(input_data)

    def check_execute(self, query: Dict[str, Any]):
        
        return self.inference_api.check_execute(query)

    def get_current_estimates(self):
        return self.inference_api.get_current_estimates()

class DefaultWebhook:

    def __init__(self, url: str, method: str = "POST", headers: Dict[str, str] = None, params: Dict[str, str] = None):
       
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}

        if self.method not in ["GET", "POST"]:
            raise ValueError("Method must be 'GET' or 'POST'")

    def call(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.method == "GET":
                response = requests.get(self.url, headers=self.headers, params={**self.params, **data})
            else:  # POST
                response = requests.post(self.url, headers=self.headers, params=self.params, json=data)

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            content_type = response.headers.get("Content-Type", "")

            if "application/json" in content_type:
                return {"status_code": response.status_code, "json": response.json()}
            else:
                return {"status_code": response.status_code, "text": response.text}

        except requests.exceptions.RequestException as e:
            return {"status_code": 500, "error": str(e)}

class DSLWebhook:
    def __init__(self, name: str, client):
        
        self.name = name
        self.client = client

    def call(self, data: Dict[str, Any]) -> Any:
        
        # Here you can add ACL checks or logging if needed
        return self.client.call(data)


class DSLCallback:
    def __init__(self, name: str, callback_fn: Callable[[Dict[str, Any]], Any]):
      
        self.name = name
        self.callback_fn = callback_fn

    def invoke(self, data: Dict[str, Any]) -> Any:
        
        return self.callback_fn(data)


class AddonsManager:
    def __init__(self):
        self.webhooks: Dict[str, DSLWebhook] = {}
        self.callbacks: Dict[str, DSLCallback] = {}

    def register_webhook(self, webhook: DSLWebhook):
        if webhook.name in self.webhooks:
            raise ValueError(f"Webhook with name '{webhook.name}' is already registered.")
        self.webhooks[webhook.name] = webhook

    def get_webhook(self, name: str) -> Optional[DSLWebhook]:
        return self.webhooks.get(name)

    def register_callback(self, callback: DSLCallback):
        if callback.name in self.callbacks:
            raise ValueError(f"Callback with name '{callback.name}' is already registered.")
        self.callbacks[callback.name] = callback

    def get_callback(self, name: str) -> Optional[DSLCallback]:
        return self.callbacks.get(name)

    def invoke_webhook(self, name: str, data: Dict[str, Any]) -> Any:
        webhook = self.get_webhook(name)
        if not webhook:
            raise ValueError(f"Webhook '{name}' not found.")
        return webhook.call(data)

    def invoke_callback(self, name: str, data: Dict[str, Any]) -> Any:
        callback = self.get_callback(name)
        if not callback:
            raise ValueError(f"Callback '{name}' not found.")
        return callback.invoke(data)
    
    def register_inference_addon(self, addon: DSLInferenceAddon):
        if addon.name in self.inference_addons:
            raise ValueError(f"Inference addon with name '{addon.name}' is already registered.")
        self.inference_addons[addon.name] = addon

    def get_inference_addon(self, name: str) -> Optional[DSLInferenceAddon]:
        return self.inference_addons.get(name)

    def invoke_inference(self, name: str, input_data: Dict[str, Any]) -> str:
        addon = self.get_inference_addon(name)
        if not addon:
            raise ValueError(f"Inference addon '{name}' not found.")
        return addon.run_inference(input_data)

    def check_inference_execute(self, name: str, query: Dict[str, Any]):
        addon = self.get_inference_addon(name)
        if not addon:
            raise ValueError(f"Inference addon '{name}' not found.")
        return addon.check_execute(query)

    def get_inference_estimates(self, name: str):
        addon = self.get_inference_addon(name)
        if not addon:
            raise ValueError(f"Inference addon '{name}' not found.")
        return addon.get_current_estimates()