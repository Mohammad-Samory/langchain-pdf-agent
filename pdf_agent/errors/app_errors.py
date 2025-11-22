from dataclasses import dataclass
from typing import Any


@dataclass
class AppError:
    code: str = ''
    message: str = ''
    field: str | None = None
    detail: str | None = None
    description: str | None = None


class ErrorMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]) -> type:
        attr_names = set()

        # Iterate over the class attributes
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, AppError):
                if attr_name in attr_names:
                    raise ValueError(f"Duplicate attribute name '{attr_name}' in class '{name}'")
                attr_names.add(attr_name)

                # Update the `code` field to match the attribute name
                attr_value.code = attr_name
        return super().__new__(cls, name, bases, dct)


class Errors(metaclass=ErrorMeta):
    # Generic errors
    FIELD_ERROR = AppError(
        message='Invalid value for $field',
        description='This error occurs when the provided value for a specific field does not meet the expected format, '
                    'type, or constraints'
    )
    VALIDATION_ERROR = AppError(
        message='Invalid request, please check the provided inputs',
        description='This error is triggered when the request contains invalid or missing data, preventing proper '
                    'processing'
    )
    REQUEST_BODY_INVALID_ERROR = AppError(
        message='The request body contains invalid JSON',
        description='Occurs when the request body cannot be parsed as valid JSON, often due to syntax errors or '
                    'incorrect formatting'
    )
    FORBIDDEN_ERROR = AppError(
        message='You do not have permission to perform this action',
        description='This error is returned when the user attempts to access a resource or perform an action they are '
                    'not authorized for'
    )
    RESOURCE_NOT_FOUND_ERROR = AppError(
        message='The requested resource could not be found',
        description='Triggered when a requested resource does not exist or has been removed'
    )
    METHOD_NOT_ALLOWED_ERROR = AppError(
        message='The requested HTTP method is not allowed for this resource',
        description='Occurs when a client attempts to use an HTTP method that is not supported by '
                    'the requested endpoint'
    )
    EXTERNAL_SERVICE_ERROR = AppError(
        message='An error occurred while communicating with an external service',
        description='This error occurs when a failure happens while interacting with an external API or service, often '
                    'due to network issues or service unavailability'
    )
    DATABASE_ERROR = AppError(
        message='An error occurred while interacting with the database',
        description='Triggered when a database operation fails due to constraints, connection issues, or unexpected '
                    'errors in queries'
    )
    SERVER_ERROR = AppError(
        message='An error occurred while processing your request, please try again later',
        description='A generic server side error that occurs when an unexpected issue prevents the request from being '
                    'processed successfully'
    )

# employees erros
    EMAIL_ALREADY_EXISTS_ERROR = AppError(
        message='Email address already exists',
        description='This error occurs when the email address is already registered in the system'
    )

    UNIT_NOT_VIRTUAL_ERROR = AppError(
        message='Must be assigned to virtual unit',
        description='This error occurs when an employee is assigned to a non-virtual legal unit'
    )

    MANAGED_BY_SELF_ERROR = AppError(
        message='Cannot be self-managed',
        description='This error occurs when an employee is set as their own manager'
    )

    JOB_TITLE_SUPERVISION_ERROR = AppError(
        message='Invalid supervision hierarchy',
        description='This error occurs when the manager\'s job title cannot supervise the employee\'s job title'
    )

    LEGAL_UNIT_MISMATCH_ERROR = AppError(
        message='Legal unit mismatch',
        description='This error occurs when the employee and manager belong to different legal units'
    )

    REPORTS_TO_SELF_ERROR = AppError(
        message='Cannot report to self',
        description='This error occurs when an employee is set to report to themselves'
    )

    INVALID_REPORTS_TO_TARGET = AppError(
        message='Invalid report target',
        description='This error occurs when the specified report-to employee is invalid or non-existent'
    )

# Job title errors
    JOB_TITLE_SELF_PARENT_ERROR = AppError(
        message='Job title cannot be its own parent',
        description='This error occurs when a job title is set as its own parent'
    )

    HIERARCHY_CYCLE_ERROR = AppError(
        message='Invalid hierarchy relationship',
        description='This error occurs when a circular dependency is detected in job title relationships'
    )

    EMPLOYEES_EXIST_ERROR = AppError(
        message='Job title has assigned employees',
        description='This error occurs when modifying a job title with active employee assignments'
    )

    JOB_TITLE_HAS_CHILDREN_ERROR = AppError(
        message='Job title has dependent titles',
        description='This error occurs when deleting a job title that has child titles'
    )

    INVALID_HIERARCHY_ERROR = AppError(
        message='Invalid job title hierarchy',
        description='This error occurs when an invalid parent-child relationship is established'
    )
