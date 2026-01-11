"""Base authentication provider interface."""

from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Request

from ..identity import Identity


class AuthProvider(ABC):
    """
    Base class for authentication providers.

    Each provider implements a specific authentication method (API key, JWT, etc.)
    and produces a unified Identity object on successful authentication.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging/debugging."""
        pass

    @abstractmethod
    def can_handle(self, request: Request) -> bool:
        """
        Check if this provider should attempt to handle the request.

        Returns True if the request contains credentials this provider understands.
        """
        pass

    @abstractmethod
    async def authenticate(self, request: Request) -> Optional[Identity]:
        """
        Attempt to authenticate the request.

        Returns:
            Identity if authentication successful
            None if this provider cannot handle the request

        Raises:
            HTTPException for authentication failures (invalid token, expired, etc.)
        """
        pass
