"""WaveSpeed API — Python client. See README.md."""
from .client import Client, run, ModelError, PredictionTimeout, MODELS, DEFAULT_MODEL

__version__ = "0.1.0"
__all__ = ["Client", "run", "ModelError", "PredictionTimeout", "MODELS", "DEFAULT_MODEL", "__version__"]
