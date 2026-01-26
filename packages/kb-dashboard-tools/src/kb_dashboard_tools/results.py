"""Generic Result pattern for consistent success/error handling across operations."""

from collections.abc import Callable
from typing import TypeVar

__all__ = ['Result']

T = TypeVar('T')
U = TypeVar('U')


class Result[T]:
    """Generic result type for operations that may succeed or fail.

    Provides a type-safe way to handle success/error cases without exceptions.
    Inspired by Rust's Result type and functional programming patterns.

    Examples:
        >>> # Success case
        >>> result = Result.ok(42)
        >>> result.success
        True
        >>> result.unwrap()
        42

        >>> # Error case
        >>> result = Result.fail('Something went wrong')
        >>> result.success
        False
        >>> result.error
        'Something went wrong'
        >>> result.unwrap_or(0)
        0

        >>> # Mapping values
        >>> result = Result.ok(5)
        >>> doubled = result.map(lambda x: x * 2)
        >>> doubled.unwrap()
        10
    """

    def __init__(self, success: bool, value: T | None = None, error: str | None = None) -> None:
        """Initialize a Result.

        Args:
            success: Whether the operation succeeded
            value: The success value (required if success=True)
            error: The error message (required if success=False)
        """
        self.success: bool = success
        self.value: T | None = value
        self.error: str | None = error

    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        """Create a successful result with a value.

        Args:
            value: The success value

        Returns:
            Result instance with success=True and the provided value
        """
        return cls(success=True, value=value, error=None)

    @classmethod
    def fail(cls, error_msg: str) -> 'Result[T]':
        """Create a failed result with an error message.

        Args:
            error_msg: The error message describing the failure

        Returns:
            Result instance with success=False and the provided error message
        """
        return cls(success=False, value=None, error=error_msg)

    def unwrap(self) -> T:
        """Get the success value, raising ValueError if this is an error result.

        Returns:
            The success value

        Raises:
            ValueError: If this is an error result
        """
        if self.success is not True or self.value is None:
            msg = f'Called unwrap() on error result: {self.error}'
            raise ValueError(msg)
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the success value, or return a default if this is an error result.

        Args:
            default: The default value to return on error

        Returns:
            The success value if successful, otherwise the default value
        """
        if self.success is True and self.value is not None:
            return self.value
        return default

    def map(self, fn: Callable[[T], U]) -> 'Result[U]':
        """Apply a function to the success value, propagating errors.

        Args:
            fn: Function to apply to the success value

        Returns:
            New Result with the transformed value if successful,
            otherwise a new error Result with the same error message
        """
        if self.success is True and self.value is not None:
            return Result.ok(fn(self.value))  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
        return Result.fail(self.error if self.error is not None else 'Unknown error')  # pyright: ignore[reportUnknownVariableType]
