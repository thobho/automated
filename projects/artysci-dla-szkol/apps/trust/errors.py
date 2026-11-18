"""Typed errors of the legal documents service."""


class LegalDocumentError(Exception):
    """Base class for legal document errors."""


class NoPublishedVersion(LegalDocumentError):
    """A kind has no published version yet, so nothing can be shown or accepted."""

    def __init__(self, kind: str):
        self.kind = kind
        super().__init__(f"no published version of {kind!r}")


class DocumentImmutable(LegalDocumentError):
    """A published version cannot be changed; a correction is a new version."""


class UnknownKind(LegalDocumentError, ValueError):
    """The kind is not one of LegalDocument.Kind."""

    def __init__(self, kind: str):
        self.kind = kind
        super().__init__(f"unknown legal document kind {kind!r}")
