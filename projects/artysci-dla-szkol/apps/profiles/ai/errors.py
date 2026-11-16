"""Typed errors of the AI adapter. Callers catch `AIError` or a specific subclass."""


class AIError(Exception):
    """Base class for every AI adapter error."""


class AIConfigError(AIError):
    """The adapter is misconfigured (missing key, unknown client, bad prices)."""


class AIDisabled(AIError):
    """The kill switch is on: no AI call is made."""


class AICapExceeded(AIError):
    """A cost cap (per call or daily) would be exceeded: no request is sent."""


class AIProviderError(AIError):
    """The provider answered with an error, timed out or sent an unusable response.

    `code` is short and safe to store (no prompt text). `maybe_billed` is True when the request
    may have been processed (timeouts), so its reserved cost is kept.
    """

    def __init__(self, message: str, *, code: str = "provider_error", maybe_billed=False):
        super().__init__(message)
        self.code = code
        self.maybe_billed = maybe_billed
