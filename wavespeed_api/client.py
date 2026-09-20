"""WaveSpeed API client — thin, dependency-light wrapper over the Synexa prediction API.

Every call creates a prediction, polls it until it settles, and returns the output.
Set SYNEXA_API_KEY in your environment or pass api_key= to Client().
"""
from __future__ import annotations
import os, time, json
from typing import Any, Dict, Optional
import httpx

API_BASE = os.environ.get("SYNEXA_API_BASE", "https://api.synexa.ai")
DEFAULT_MODEL = "black-forest-labs/flux-schnell"
MODELS = {
    "black-forest-labs/flux-schnell": {
        "category": "text-to-image",
        "price_usd": 0.0015,
        "required": [
            "prompt"
        ],
        "fields": [
            "seed",
            "prompt",
            "go_fast",
            "megapixels",
            "num_outputs",
            "aspect_ratio",
            "output_format",
            "output_quality",
            "num_inference_steps",
            "disable_safety_checker"
        ],
        "url": "https://synexa.ai/explore/black-forest-labs/flux-schnell"
    },
    "tongyi/wan2.2": {
        "category": "image-to-video",
        "price_usd": 0.2,
        "required": [
            "prompt",
            "input_image"
        ],
        "fields": [
            "prompt",
            "input_image",
            "aspect_ratio",
            "seed",
            "num_frames"
        ],
        "url": "https://synexa.ai/explore/tongyi/wan2.2"
    },
    "bytedance/seedance-2.5": {
        "category": "text-to-video",
        "price_usd": 0.473,
        "required": [
            "prompt"
        ],
        "fields": [
            "prompt",
            "resolution",
            "duration",
            "aspect_ratio",
            "generate_audio",
            "bitrate_mode"
        ],
        "url": "https://synexa.ai/explore/bytedance/seedance-2.5"
    }
}

__all__ = ["Client", "run", "ModelError", "PredictionTimeout", "MODELS", "DEFAULT_MODEL"]


class ModelError(RuntimeError):
    """The prediction finished with status=failed."""
    def __init__(self, message: str, prediction: Optional[dict] = None):
        super().__init__(message)
        self.prediction = prediction


class PredictionTimeout(TimeoutError):
    pass


class Client:
    def __init__(self, api_key: Optional[str] = None, base_url: str = API_BASE, timeout: float = 60.0):
        self.api_key = api_key or os.environ.get("SYNEXA_API_KEY")
        if not self.api_key:
            raise ValueError("Missing API key: set SYNEXA_API_KEY or pass api_key=")
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(timeout=timeout, headers={"x-api-key": self.api_key, "user-agent": "wavespeed_api/0.1.0"})

    # -- low level -----------------------------------------------------------------
    def create(self, input: Dict[str, Any], model: str = DEFAULT_MODEL, webhook: Optional[str] = None) -> dict:
        body = {"model": model, "input": input}
        if webhook:
            body["webhook"] = webhook
        r = self._http.post(f"{self.base_url}/v1/predictions", json=body)
        if r.status_code >= 400:
            raise ModelError(f"{r.status_code}: {r.text[:300]}")
        return r.json()

    def get(self, prediction_id: str) -> dict:
        r = self._http.get(f"{self.base_url}/v1/predictions/{prediction_id}")
        r.raise_for_status()
        return r.json()

    def wait(self, prediction: dict, timeout: float = 600, interval: float = 2.0) -> dict:
        deadline = time.time() + timeout
        while prediction.get("status") not in ("succeeded", "failed"):
            if time.time() > deadline:
                raise PredictionTimeout(f"prediction {prediction.get('id')} still {prediction.get('status')} after {timeout}s")
            time.sleep(interval)
            prediction = self.get(prediction["id"])
        if prediction["status"] == "failed":
            raise ModelError(prediction.get("error") or "prediction failed", prediction)
        return prediction

    # -- high level ----------------------------------------------------------------
    def run(self, input: Dict[str, Any], model: str = DEFAULT_MODEL, wait: bool | float = True, webhook: Optional[str] = None):
        """Create a prediction and (by default) block until it finishes. Returns the model output."""
        pred = self.create(input, model=model, webhook=webhook)
        if wait is False:
            return pred
        pred = self.wait(pred, timeout=600 if wait is True else float(wait))
        return pred.get("output")

    def model_info(self, model: str = DEFAULT_MODEL) -> dict:
        owner, name = model.split("/", 1)
        r = self._http.get(f"{self.base_url}/models/{owner}/{name}")
        r.raise_for_status()
        return r.json()


_default: Optional[Client] = None


def run(input: Dict[str, Any], model: str = DEFAULT_MODEL, **kw):
    """Module-level shortcut: `wavespeed_api.run({...})` using SYNEXA_API_KEY from the environment."""
    global _default
    if _default is None:
        _default = Client()
    return _default.run(input, model=model, **kw)
