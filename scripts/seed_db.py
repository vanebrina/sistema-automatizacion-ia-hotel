"""Crea las tablas y siembra las reservas de ejemplo.

Uso:
    python -m scripts.seed_db          # siembra si está vacío
    python -m scripts.seed_db --force  # reinserta siempre
"""

from __future__ import annotations

import argparse

from app.core.logging import setup_logging
from app.db.base import init_db, session_scope
from app.db.seed import seed_reservations


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Siembra de reservas del hotel.")
    parser.add_argument("--force", action="store_true", help="Reinsertar aunque ya existan.")
    args = parser.parse_args()

    init_db()
    with session_scope() as session:
        inserted = seed_reservations(session, force=args.force)
    print(f"Reservas insertadas: {inserted}")


if __name__ == "__main__":
    main()
