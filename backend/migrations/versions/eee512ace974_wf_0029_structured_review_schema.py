"""wf-0029 structured review schema

Revision ID: eee512ace974
Revises: 1c4d8f7a9c23
Create Date: 2026-02-22 14:32:36.970865

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eee512ace974'
down_revision: str | Sequence[str] | None = '1c4d8f7a9c23'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    assessment_status_enum = sa.Enum(
        "ASSESSED",
        "NOT_ASSESSABLE",
        name="assessmentstatus",
    )
    assessment_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "review_cards",
        sa.Column(
            "assessment_status",
            assessment_status_enum,
            nullable=False,
            server_default="ASSESSED",
        ),
    )
    op.add_column(
        "review_cards",
        sa.Column("not_assessable_reason", sa.String(), nullable=True),
    )
    op.add_column(
        "reviews",
        sa.Column("review_type", sa.String(), nullable=False, server_default="single"),
    )
    op.add_column(
        "reviews",
        sa.Column("structured_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.alter_column(
        "reviews",
        "proposal_snippet_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "reviews",
        "proposal_snippet_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_column("reviews", "structured_payload")
    op.drop_column("reviews", "review_type")
    op.drop_column("review_cards", "not_assessable_reason")
    op.drop_column("review_cards", "assessment_status")
    sa.Enum(name="assessmentstatus").drop(op.get_bind(), checkfirst=True)
