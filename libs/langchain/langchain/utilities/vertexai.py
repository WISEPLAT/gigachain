"""Utilities to init Vertex AI."""
from importlib import metadata
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from langchain_core.language_models.llms import BaseLLM, create_base_retry_decorator

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)

if TYPE_CHECKING:
    from google.api_core.gapic_v1.client_info import ClientInfo
    from google.auth.credentials import Credentials


def create_retry_decorator(
    llm: BaseLLM,
    *,
    max_retries: int = 1,
    run_manager: Optional[
        Union[AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun]
    ] = None,
) -> Callable[[Any], Any]:
    """Creates a retry decorator for Vertex / Palm LLMs."""
    import google.api_core

    errors = [
        google.api_core.exceptions.ResourceExhausted,
        google.api_core.exceptions.ServiceUnavailable,
        google.api_core.exceptions.Aborted,
        google.api_core.exceptions.DeadlineExceeded,
        google.api_core.exceptions.GoogleAPIError,
    ]
    decorator = create_base_retry_decorator(
        error_types=errors, max_retries=max_retries, run_manager=run_manager
    )
    return decorator


def raise_vertex_import_error(minimum_expected_version: str = "1.36.0") -> None:
    """Raise ImportError related to Vertex SDK being not available.

    Args:
        minimum_expected_version: The lowest expected version of the SDK.
    Raises:
        ImportError: an ImportError that mentions a required version of the SDK.
    """
    raise ImportError(
        "Please, install or upgrade the google-cloud-aiplatform library: "
        f"pip install google-cloud-aiplatform>={minimum_expected_version}"
    )


def init_vertexai(
    project: Optional[str] = None,
    location: Optional[str] = None,
    credentials: Optional["Credentials"] = None,
) -> None:
    """Init vertexai.

    Args:
        project: The default GCP project to use when making Vertex API calls.
        location: The default location to use when making API calls.
        credentials: The default custom
            credentials to use when making API calls. If not provided credentials
            will be ascertained from the environment.

    Raises:
        ImportError: If importing vertexai SDK did not succeed.
    """
    try:
        import vertexai
    except ImportError:
        raise_vertex_import_error()

    vertexai.init(
        project=project,
        location=location,
        credentials=credentials,
    )


def get_client_info(module: Optional[str] = None) -> "ClientInfo":
    r"""Returns a custom user agent header.

    Args:
        module (Optional[str]):
            Optional. The module for a custom user agent header.
    Returns:
        google.api_core.gapic_v1.client_info.ClientInfo
    """
    try:
        from google.api_core.gapic_v1.client_info import ClientInfo
    except ImportError as exc:
        raise ImportError(
            "Could not import ClientInfo. Please, install it with "
            "pip install google-api-core"
        ) from exc

    gigachain_version = metadata.version("gigachain")
    client_library_version = (
        f"{gigachain_version}-{module}" if module else gigachain_version
    )
    return ClientInfo(
        client_library_version=client_library_version,
        user_agent=f"langchain/{client_library_version}",
    )
