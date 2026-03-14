"""backend/migrations/versions/6f8d4c8d91c2_wf0079_review_card_companion_text.py

wf-0079 review_card companion text

Revision ID: 6f8d4c8d91c2
Revises: eee512ace974
Create Date: 2026-03-14 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f8d4c8d91c2"
down_revision: str | Sequence[str] | None = "eee512ace974"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "review_cards",
        sa.Column("synthesized_companion_text", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("review_cards", "synthesized_companion_text")
