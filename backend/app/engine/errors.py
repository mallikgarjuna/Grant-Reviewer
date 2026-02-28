from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EngineErrorCode(StrEnum):
    CALL_CONFIG_DIGEST_MISMATCH = "CALL_CONFIG_DIGEST_MISMATCH"
    MALFORMED_REVIEW_REQUEST = "MALFORMED_REVIEW_REQUEST"
    EXPECTATION_REF_UNRESOLVABLE = "EXPECTATION_REF_UNRESOLVABLE"
    ENGINE_EXECUTION_FAILED = "ENGINE_EXECUTION_FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass(frozen=True)
class EngineError:
    code: EngineErrorCode
    message: str


class EngineContractError(ValueError):
    def __init__(self, *, code: EngineErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code.value}: {message}")


class EngineExecutionError(RuntimeError):
    def __init__(self, *, code: EngineErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code.value}: {message}")
