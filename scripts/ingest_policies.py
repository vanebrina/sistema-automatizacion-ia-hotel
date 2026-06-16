"""Vectoriza las políticas del hotel en PGVector (RAG).

Uso:
    python -m scripts.ingest_policies          # indexa si la colección está vacía
    python -m scripts.ingest_policies --force  # reindexa siempre
"""

from __future__ import annotations

import argparse

from app.core.logging import setup_logging
from app.rag.retriever import ingest_policies


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Ingesta de políticas del hotel (RAG).")
    parser.add_argument("--force", action="store_true", help="Reindexar aunque ya exista.")
    args = parser.parse_args()

    n = ingest_policies(force=args.force)
    print(f"Fragmentos indexados: {n}")


if __name__ == "__main__":
    main()
