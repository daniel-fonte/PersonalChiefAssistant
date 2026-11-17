"""Configuration loaded from environment variables."""

import os


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"A variável de ambiente {name} não foi definida.")
    return value
