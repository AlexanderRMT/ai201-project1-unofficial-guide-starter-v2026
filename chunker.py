"""
Stage 2: paragraph chunks with title context for the campus_life posts.

The original fixed-window strategy remains as fallback_split for comparison.
To reproduce the starter baseline, pass chunk_size=800 and overlap=120.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = config.CHUNK_SIZE if chunk_size is None else chunk_size
    overlap = config.CHUNK_OVERLAP if overlap is None else overlap

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and 0 <= overlap < chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """Keep each campus post's paragraphs intact and repeat its title.

    CHUNK_SIZE is a soft character ceiling including the repeated title.
    Long paragraphs are packed by sentence, with zero body overlap. A single
    oversized sentence is retained whole instead of losing its context.
    The corpus's paragraphs fit below the ceiling, so no sentence splitting
    is needed for campus_life. A single-block document is treated as body.
    """
    if config.CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be positive")

    chunks: list[Chunk] = []
    for doc in documents:
        blocks = [block.strip() for block in re.split(r"\n\s*\n", doc.text) if block.strip()]
        if not blocks:
            continue
        title = ""
        if len(blocks) > 1 and "\n" not in blocks[0] and len(blocks[0]) <= 120:
            title = blocks.pop(0) + "\n\n"

        pieces: list[str] = []
        for paragraph in blocks:
            if len(title) + len(paragraph) <= config.CHUNK_SIZE:
                pieces.append(paragraph)
                continue

            current = ""
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
                candidate = f"{current} {sentence}" if current else sentence
                if current and len(title) + len(candidate) > config.CHUNK_SIZE:
                    pieces.append(current)
                    current = sentence
                else:
                    current = candidate
            if current:
                pieces.append(current)

        for index, piece in enumerate(pieces):
            chunks.append(Chunk(title + piece, doc.source, index, "chunker.py::split_documents"))
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
