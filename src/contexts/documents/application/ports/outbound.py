"""
src/contexts/documents/application/ports/outbound.py
======================================================
FIX 5: DocumentRepository is split into cheap metadata ops and expensive content ops.

This makes the cost boundary explicit and prevents ORM eager-loading of
megabytes of text on every document list or status check.
"""
from __future__ import annotations

from typing import Protocol

from src.shared_kernel.domain.identity import DocumentId, StudentId
from src.contexts.documents.domain.entities import (
    Document,
    DocumentContent,
    FileType,
    QASession,
)


class DocumentRepository(Protocol):
    """Two tiers: metadata (always cheap) and content (expensive, explicit)."""

    # ── Metadata operations — always fast, safe to call anywhere ──

    async def save_metadata(self, doc: Document) -> None: ...

    async def get_metadata(self, id: DocumentId) -> Document | None:
        """Load metadata only. Never loads text content."""
        ...

    async def list_by_owner(self, owner_id: StudentId) -> list[Document]:
        """List all documents for a student. Metadata only."""
        ...

    # ── Content operations — expensive, only called by AskQuestionUseCase ──

    async def save_content(self, doc_id: DocumentId, content: DocumentContent) -> None:
        """Store extracted text chunks. Called once after processing."""
        ...

    async def get_content(self, id: DocumentId) -> DocumentContent | None:
        """Load full text chunks. ONLY called by AskQuestionUseCase.
        Never call this from list operations or status checks.
        """
        ...


class QASessionRepository(Protocol):
    async def save(self, session: QASession) -> None: ...
    async def get_by_document(self, document_id: DocumentId) -> QASession | None: ...


class FileStoragePort(Protocol):
    """Raw file bytes storage — S3, MinIO, or local filesystem."""
    async def upload(self, key: str, data: bytes) -> str: ...
    async def download(self, key: str) -> bytes: ...


class TextExtractorPort(Protocol):
    """Extract plain text from a file. Implemented per file type."""
    async def extract(self, file_type: FileType, data: bytes) -> str: ...


class LLMPort(Protocol):
    """Answer a question given retrieved context chunks."""
    async def answer(self, context_chunks: list[str], question: str) -> str: ...
