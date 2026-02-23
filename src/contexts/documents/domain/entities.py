"""
src/contexts/documents/domain/entities.py
==========================================
FIX 5: Document.text_content: str | None REMOVED from the aggregate.

Why it was wrong:
  - A 50 MB PDF extracts to a very large string.
  - Storing it on the aggregate means EVERY load of Document (status check,
    file listing, anything) hydrates megabytes of text via ORM eager loading.
  - A student listing their 10 documents would trigger 10 × (up to 50 MB) reads.

Fix: Document holds metadata only. Text content lives in DocumentContent,
     a separate value object loaded ONLY by AskQuestionUseCase.

Repository reflects this:
    DocumentRepository.get_metadata(id)  → Document       (cheap, always)
    DocumentRepository.get_content(id)   → DocumentContent (expensive, AskQuestion only)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from src.shared_kernel.domain.identity import DocumentId, StudentId


class FileType(Enum):
    PDF = "pdf"
    DOCX = "docx"


class DocumentStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# FIX 5A — Document aggregate (metadata only, always cheap to load)
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """Aggregate root: document metadata.

    Never contains extracted text. Always safe to load for listing/status checks.
    """
    id: DocumentId
    owner_id: StudentId
    filename: str
    file_type: FileType
    storage_key: str          # opaque S3/local key — text never stored here
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: datetime | None = None

    # NO text_content field

    @classmethod
    def upload(
        cls,
        owner_id: StudentId,
        filename: str,
        file_type: FileType,
        storage_key: str,
    ) -> "Document":
        return cls(
            id=DocumentId(uuid4()),
            owner_id=owner_id,
            filename=filename,
            file_type=file_type,
            storage_key=storage_key,
            status=DocumentStatus.UPLOADED,
            uploaded_at=datetime.utcnow(),
        )

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING

    def mark_ready(self) -> None:
        self.status = DocumentStatus.READY
        self.processed_at = datetime.utcnow()

    def mark_failed(self) -> None:
        self.status = DocumentStatus.FAILED


# ---------------------------------------------------------------------------
# FIX 5B — DocumentContent: loaded only when answering a question
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TextChunk:
    """One chunk of extracted text, used as RAG context."""
    chunk_index: int
    content: str
    token_count: int = 0


@dataclass(frozen=True)
class DocumentContent:
    """Extracted and chunked text for a document.

    Loaded ONLY by AskQuestionUseCase.
    Fetched via DocumentRepository.get_content(id) — a separate, explicit call.
    Never returned by list_by_owner() or get_metadata().
    """
    document_id: DocumentId
    chunks: tuple[TextChunk, ...]

    @property
    def full_text(self) -> str:
        return "\n".join(c.content for c in self.chunks)

    def top_chunks(self, n: int = 5) -> list[str]:
        """Return first n chunk contents as context for the LLM."""
        return [c.content for c in self.chunks[:n]]


# ---------------------------------------------------------------------------
# QA Session aggregate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QAExchange:
    """One question-answer pair within a session."""
    question: str
    answer: str
    asked_at: datetime
    source_chunk_indices: tuple[int, ...] = field(default_factory=tuple)


@dataclass
class QASession:
    """Aggregate root: a student's Q&A history for one document."""
    id: UUID
    document_id: DocumentId
    student_id: StudentId
    exchanges: list[QAExchange] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def start(cls, document_id: DocumentId, student_id: StudentId) -> "QASession":
        return cls(id=uuid4(), document_id=document_id, student_id=student_id)

    def add_exchange(self, question: str, answer: str, source_indices: tuple[int, ...] = ()) -> None:
        self.exchanges.append(
            QAExchange(
                question=question,
                answer=answer,
                asked_at=datetime.utcnow(),
                source_chunk_indices=source_indices,
            )
        )
