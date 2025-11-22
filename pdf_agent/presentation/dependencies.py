from collections.abc import Callable
from typing import Any, overload

from pdf_agent.application.base_service import BaseService
from pdf_agent.configs.log import get_logger

logger = get_logger()

# Singleton storage for service instances
_service_instances: dict[type, Any] = {}


@overload
def get_service(
    service_class: type[BaseService]
) -> Callable[..., BaseService]:
    ...


@overload
def get_service(service_class: type[Any]) -> Callable[..., Any]:
    ...


def get_service(service_class: type[Any]) -> Callable[..., Any]:
    """Factory returning a FastAPI dependency that injects the requested service as a singleton."""

    def service_dependency() -> Any:
        if issubclass(service_class, BaseService):
            # Return existing instance or create new one
            if service_class not in _service_instances:
                _service_instances[service_class] = service_class()
                logger.info(f"Created new singleton instance of {service_class.__name__}")
            return _service_instances[service_class]
        raise ValueError(f'Unsupported service class: {service_class}')

    return service_dependency
