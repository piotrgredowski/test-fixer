import openai
import dotenv


def _get_key():
    return dotenv.get_key(".env", "OPENAI_API_KEY")


def get_openai_backend():
    openai.api_key = _get_key()
    return openai


_AZURE_BACKEND = "azure"


def get_azure_backend():
    openai.api_key = _get_key()
    openai.api_type = _AZURE_BACKEND
    openai.api_base = dotenv.get_key(".env", "OPENAI_API_BASE")
    openai.api_version = dotenv.get_key(".env", "OPENAI_API_VERSION")
    return openai


def set_backend():
    """
    Set the correct backend to be used - either Azure or OpenAI,
    using "BACKEND_TO_USE" variable from .env file.

    Set the correct API key to be used using "OPENAI_API_KEY" variable from .env file,
    """
    backend_name = dotenv.get_key(".env", "BACKEND_TO_USE")
    if not backend_name:
        get_backend = get_azure_backend
    else:
        _MAP = {
            _AZURE_BACKEND: get_azure_backend,
            "openai": get_openai_backend,
        }
        get_backend = _MAP.get(backend_name, get_azure_backend)
    backend = get_backend()
    backend.api_key = _get_key()
