"""Authentication and authorization package."""

from .identity import Identity, AuthMethod
from .config import AuthConfig
from .chain import AuthChain
from .dependencies import (
    get_auth_config,
    get_auth_chain,
    get_current_identity,
    CurrentIdentity,
    require_scope,
    require_client,
    reset_auth_config,
)

__all__ = [
    "Identity",
    "AuthMethod",
    "AuthConfig",
    "AuthChain",
    "get_auth_config",
    "get_auth_chain",
    "get_current_identity",
    "CurrentIdentity",
    "require_scope",
    "require_client",
    "reset_auth_config",
]
