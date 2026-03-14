"""backend/migrations/versions/2d4af27c7f3d_wf0081_review_findings_detail_mode.py

wf-0081 review findings detail mode

Revision ID: 2d4af27c7f3d
Revises: 6f8d4c8d91c2
Create Date: 2026-03-14 15:05:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2d4af27c7f3d"
down_revision: str | Sequence[str] | None = "6f8d4c8d91c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_enum
                WHERE enumlabel = 'REQUIREMENTS_MET'
                  AND enumtypid = 'assessmentstatus'::regtype
            ) THEN
                ALTER TYPE assessmentstatus ADD VALUE 'REQUIREMENTS_MET';
            END IF;
        END
        $$;
        """
    )

    op.add_column(
        "reviews",
        sa.Column(
            "detail_mode",
            sa.String(),
            nullable=False,
            server_default="legacy_cards",
        ),
    )

    op.create_table(
        "review_findings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("review_id", sa.UUID(), nullable=False),
        sa.Column("proposal_node_id", sa.UUID(), nullable=False),
        sa.Column(
            "proposal_node_logical_id_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "proposal_node_title_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "evaluation_criterion_logical_id_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "evaluation_criterion_name_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "evaluation_element_logical_id_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "evaluation_element_name_snapshot",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM(name="reviewrating", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "assessment_status",
            postgresql.ENUM(name="assessmentstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("issue_summary_text", sa.String(), nullable=False),
        sa.Column("evidence_basis_text", sa.String(), nullable=False),
        sa.Column("actionable_feedback_text", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["proposal_node_id"], ["proposal_nodes.id"]),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("review_findings")
    op.drop_column("reviews", "detail_mode")
