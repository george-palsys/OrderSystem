"""Custom exceptions for order system domain logic."""


class DomainError(Exception):
    """Base class for domain-specific errors."""


class ValidationError(DomainError):
    """Raised when incoming data is invalid."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class BusinessRuleError(DomainError):
    """Raised when domain rules prevent an operation."""
