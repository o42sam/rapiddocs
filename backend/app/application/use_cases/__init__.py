"""
Application use cases.
Orchestrate domain logic and infrastructure services.
"""

from .generate_invoice import GenerateInvoiceUseCase
from .register_user import RegisterUserUseCase
from .login_user import LoginUserUseCase
# Future use cases to be implemented:
# from .generate_infographic import GenerateInfographicUseCase
# from .generate_formal import GenerateFormalDocumentUseCase
# from .import_data import ImportDataUseCase
# from .check_job_status import CheckJobStatusUseCase

__all__ = [
    "GenerateInvoiceUseCase",
    "RegisterUserUseCase",
    "LoginUserUseCase"
]